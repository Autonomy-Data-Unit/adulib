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
except ImportError as e:
    raise ImportError(f"Install adulib[{__name__.split('.')[-1]}] to use this API.") from e

# %%
import adulib.llm

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
