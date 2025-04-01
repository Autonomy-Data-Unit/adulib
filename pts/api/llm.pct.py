# %% [markdown]
# # adulib.llm

# %%
#|default_exp llm

# %%
#|hide
import nblite; from nbdev.showdoc import show_doc; nblite.nbl_export()

# %%
#|export
try:
    import os
    import json
    import tempfile
    from pathlib import Path
    from openai import OpenAI, AsyncOpenAI
    import tiktoken
    from asynciolimiter import Limiter
    import diskcache
    from typing import List, Optional, Type, Dict, Any
    import asyncio
    import time
    from tqdm import tqdm
except ImportError as e:
    raise ImportError(f"Install adulib[{__name__.split('.')[-1]}] to use this API.") from e

# %%
from dotenv import load_dotenv

# %%
import adulib.llm

# %%
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# %%
#|export
model_context_windows = {
    'gpt-4o': 128000 * 0.8,
    'gpt-4o-mini': 128000 * 0.8,
}

model_rate_limits = {
    'gpt-4o': 10000,
    'gpt-4o-mini': 30000,
}

# %%
show_doc(adulib.llm.tokenize_text)

# %%
#|export
__model_tokenisers = {}

def tokenize_text(text, llm_model):
    if llm_model not in __model_tokenisers:
        __model_tokenisers[llm_model] = tiktoken.encoding_for_model(llm_model)
    return __model_tokenisers[llm_model].encode(text)


# %%
tokenize_text("hello world", 'gpt-4o')

# %%
show_doc(adulib.llm.detokenize_text)


# %%
#|export
def detokenize_text(tokens, llm_model):
    if llm_model not in __model_tokenisers:
        __model_tokenisers[llm_model] = tiktoken.encoding_for_model(llm_model)
    tokeniser_enc = tiktoken.encoding_for_model(llm_model)
    return tokeniser_enc.decode(tokens)


# %%
llm_model = 'gpt-4o'
detokenize_text(tokenize_text("hello world", llm_model), llm_model)

# %%
show_doc(adulib.llm.get_token_count)


# %%
#|export
def get_token_count(text, llm_model):
    return len(tokenize_text(text, llm_model))


# %%
get_token_count("hello world", "gpt-4o")

# %%
show_doc(adulib.llm.async_prompt)

# %%
#|export
__client = None
__model_rate_limiters = {}
__llm_cache = None

async def async_prompt(model,
                           prompt,
                           context="You are a helpful assistant.",
                           api_key=None,
                           response_format=None,
                           use_cache=True,
                           cache_dir=None,
                           include_model_in_cache_key=False,
                           cache_key_prepend=''):
    global __client, __llm_cache
    if __client is None:
        if api_key is None: api_key = os.environ.get("PROJ_OPENAI_API_KEY")
        __client = AsyncOpenAI(api_key=api_key)
        
    if model not in __model_rate_limiters:
        __model_rate_limiters[model] = Limiter(model_rate_limits[model]/60)
        
    response_schema = str(response_format.model_json_schema()) if response_format else ""
        
    if __llm_cache is None:
        if cache_dir is None: cache_dir = tempfile.mkdtemp()
        abs_cache_path = Path(cache_dir).resolve().as_posix()
        __llm_cache = diskcache.Cache(abs_cache_path, eviction_policy="none", size_limit=2**40)
    
    _model_key = model if include_model_in_cache_key else '*'
    cache_key = f'{cache_key_prepend}:{_model_key}:{prompt}:{context}:{response_schema}'
    
    if use_cache and cache_key in __llm_cache:
        output =  __llm_cache[cache_key]
    else:
        await __model_rate_limiters[model].wait()
        if not response_schema:
            chat_completion = await __client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": context
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
            )
        else:
            chat_completion = await __client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "system",
                        "content": context
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
                response_format=response_format
            )
        output = chat_completion.choices[0].message.content
        __llm_cache[cache_key] = output
    
    if response_format:
        return response_format(**json.loads(output))
    else:
        return output

# %%
await async_prompt(
    model='gpt-4o',
    context='You are a helpful assistant.',
    prompt='Hello, how are you?',
    cache_dir='./tmp/llm_cache'
)

# %%
from pydantic import BaseModel
from pprint import pprint


# %%
class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str
    
res = await async_prompt(
    model='gpt-4o',
    context='You are a helpful math tutor. Guide the user through the solution step by step.',
    prompt='How can I solve 8x + 7 = -23?',
    response_format=MathReasoning,
    cache_dir='./tmp/llm_cache'
)

pprint(res.model_dump())

# %% [markdown]
# ### async_prompts

# %%
#|export
async def async_prompts(
    model: str,
    context: str,
    items: List[str],
    prompt_template: str,
    response_format: Optional[Type[BaseModel]] = None,
    api_key: Optional[str] = None,
    cache_dir: Optional[str] = None,
    include_model_in_cache_key: bool = False,
    cache_key_prepend: str = '',
    max_retries: int = 3,
    timeout: int = 30,
    time_window = 20,
    concurrency_limit: Optional[int] = None
    ):
    semaphore = asyncio.Semaphore(concurrency_limit) if concurrency_limit else asyncio.Semaphore(len(items))
    
    async def process_item(item: str):
        prompt = prompt_template.format(item=item)

        for attempt in range(max_retries):
            async with semaphore:
                start_time = time.time()
                try:
                    task = asyncio.create_task(
                        async_prompt(
                            model=model,
                            prompt=prompt,
                            context=context,
                            response_format=response_format,
                            api_key=api_key,
                            use_cache=True,
                            cache_dir=cache_dir,
                            include_model_in_cache_key=include_model_in_cache_key,
                            cache_key_prepend=cache_key_prepend
                        )
                    )

                    done, pending = await asyncio.wait({task}, timeout=timeout)

                    if task in done:
                        return task.result()

                    else:
                        task.cancel()
                        print(f"[Timeout] '{item}' attempt {attempt + 1}/{max_retries} exceeded {timeout}s")

                except asyncio.CancelledError:
                    print(f"[Cancelled] '{item}' attempt {attempt + 1}/{max_retries}")

                except Exception as e:
                    print(f"[Error] '{item}' attempt {attempt + 1}/{max_retries}: {e}")

                await asyncio.sleep(2 ** attempt)  # exponential backoff

                elapsed = time.time() - start_time
                if elapsed < time_window:
                    await asyncio.sleep(time_window - elapsed)

        print(f"[Fail] '{item}' max retries exceeded.")
        return None

    tasks = {item: asyncio.create_task(process_item(item)) for item in items}
    output = []
    for item in tqdm(items, desc="Processing"):
        try: 
            result = await process_item(item)
            if result:
                output.append({
                    "item": item,
                    "response": result.model_dump() if hasattr(result, "model_dump") else result
                })
        except Exception as e:
            print(f"[Unhandled Error] '{item}': {e}")

    return output


# %%
class FilmRecommendation(BaseModel):
    title: str
    blurb: str
    review: str

res = await async_prompts(
    model='gpt-4o',
    context="""You are an eager member of staff at the last surviving Blockbuster store.
    Recommend a film to the user based on their stated preferences.
    You should give them the film title, the blurb in a sentence and then a quick one 
    sentence long review to hype them up for it.""",
    items = ["  a psychological horror film that will actually unsettle me",
                "  something very romantic, Y2K, nostalgic",
                "  strange, obscure and quite old",
                "  a film where I don't have to pay attention and can doomscroll on my phone"],
    prompt_template = "User preference: {item}",
    response_format=FilmRecommendation,
    cache_dir='./tmp/llm_cache'
)

# %%
res

# %%
show_doc(adulib.llm.prompt)

# %%
#|export
__client = None

def prompt(model,
                prompt,
                context="You are a helpful assistant.",
                api_key=None,
                response_format=None,
                use_cache=True,
                cache_dir=None,
                include_model_in_cache_key=False,
                cache_key_prepend=''):
    global __client, __llm_cache
    if __client is None:
        if api_key is None: api_key = os.environ.get("PROJ_OPENAI_API_KEY")
        __client = OpenAI(api_key=api_key)
        
    response_schema = str(response_format.model_json_schema()) if response_format else ""
        
    if __llm_cache is None:
        if cache_dir is None: cache_dir = tempfile.mkdtemp()
        abs_cache_path = Path(cache_dir).resolve().as_posix()
        __llm_cache = diskcache.Cache(abs_cache_path, eviction_policy="none", size_limit=2**40)
    
    _model_key = model if include_model_in_cache_key else '*'
    cache_key = f'{cache_key_prepend}:{_model_key}:{prompt}:{context}:{response_schema}'
    
    if use_cache and cache_key in __llm_cache:
        output =  __llm_cache[cache_key]
    else:
        if not response_schema:
            chat_completion = __client.chat.completions.create(  # Changed to synchronous call
                messages=[
                    {
                        "role": "system",
                        "content": context
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
            )
        else:
            chat_completion = __client.beta.chat.completions.parse(  # Changed to synchronous call
                messages=[
                    {
                        "role": "system",
                        "content": context
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
                response_format=response_format
            )
            
        output = chat_completion.choices[0].message.content
        __llm_cache[cache_key] = output
    
    if response_format:
        return response_format(**json.loads(output))
    else:
        return output


# %%
prompt(
    model='gpt-4o',
    context='You are a helpful assistant.',
    prompt='Hello, how are you?',
    cache_dir='./tmp/llm_cache'
)

# %%
