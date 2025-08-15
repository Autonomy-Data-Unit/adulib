# %% [markdown]
# # embeddings
#
# > See the [`litellm` documention](https://docs.litellm.ai/docs/embedding/supported_embedding).

# %%
#|default_exp llm.embeddings

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
import inspect
from inspect import Parameter
import asyncio
try:
    import litellm
    import functools
    from adulib.llm._utils import _llm_func_factory, _llm_async_func_factory
    from adulib.llm.tokens import token_counter
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
from adulib.caching import set_default_cache_path
import adulib.llm.embeddings as this_module

# %%
#|hide
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')

# %%
#|echo: false
show_doc(this_module.embedding)

# %%
#|export
embedding = _llm_func_factory(
    func=litellm.embedding,
    func_name="embedding",
    func_cache_name="embedding",
    module_name=__name__,
    retrieve_log_data=lambda model, func_kwargs, response, cache_args: {
        "method": "embedding",
        "input_tokens": sum([token_counter(model=model, text=inp, **cache_args) for inp in func_kwargs['input']]),
        "output_tokens": None,
        "cost": response._hidden_params['response_cost'],
    }
)

embedding.__doc__ = """
This function is a wrapper around a corresponding function in the `litellm` library, see [this](https://docs.litellm.ai/docs/embedding/supported_embedding) for a full list of the available arguments.
""".strip()
sig = inspect.signature(embedding)
sig = sig.replace(parameters=[
    Parameter("model", Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
    Parameter("input", Parameter.POSITIONAL_OR_KEYWORD, annotation=list[str]),
    *sig.parameters.values()
])
embedding.__signature__ = sig

# %%
response, cache_hit, call_log = embedding(
    model="text-embedding-3-small",
    input=[
        "First string to embsed",
        "Second string to embed",
    ],
)
response.data[1]['embedding'][:10]

# %%
#|echo: false
show_doc(this_module.async_embedding)

# %%
#|export
async_embedding = _llm_async_func_factory(
    func=functools.wraps(litellm.embedding)(litellm.aembedding), # This is needed as 'litellm.aembedding' lacks the right signature
    func_name="async_embedding",
    func_cache_name="embedding",
    module_name=__name__,
    retrieve_log_data=lambda model, func_kwargs, response, cache_args: {
        "method": "embedding",
        "input_tokens": sum([token_counter(model=model, text=inp, **cache_args) for inp in func_kwargs['input']]),
        "output_tokens": None,
        "cost": response._hidden_params['response_cost'],
    }
)

async_embedding.__doc__ = """
This function is a wrapper around a corresponding function in the `litellm` library, see [this](https://docs.litellm.ai/docs/embedding/supported_embedding) for a full list of the available arguments.
""".strip()
sig = inspect.signature(async_embedding)
sig = sig.replace(parameters=[
    Parameter("model", Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
    Parameter("input", Parameter.POSITIONAL_OR_KEYWORD, annotation=list[str]),
    *sig.parameters.values()
])
async_embedding.__signature__ = sig

# %%
response, cache_hit, call_log = await async_embedding(
    model="text-embedding-3-small",
    input=[
        "First string to embed",
        "Second string to embed",
    ],
)
response.data[1]['embedding'][:10]

# %%
#|hide
show_doc(this_module.batch_embeddings)


# %%
#|export
def batch_embeddings(
    model: str,
    input: list[str] = None,
    batch_size: int = 1000,
    verbose: bool = False,
    **kwargs
):
    """
    Compute embeddings for a list of input strings in batches synchronously.

    Args:
        model (str): The embedding model to use.
        input (list[str]): List of input strings to embed.
        batch_size (int): Number of inputs per batch.
        verbose (bool): If True, display a progress bar.
        **kwargs: Additional keyword arguments passed to `embedding`.

    Returns:
        list: List of embedding vectors for each input string.
    """
    batches = []
    for i in range(0, len(input), batch_size):
        batch = input[i:i + batch_size]
        batches.append(batch)
    
    responses = []
    if verbose:
        from tqdm import tqdm
        for batch in tqdm(batches, desc="Processing embedding batches"):
            response, cache_hit, call_log = embedding(model=model, input=batch, **kwargs)
            responses.append((response, cache_hit, call_log))
    else:
        for batch in batches:
            response, cache_hit, call_log = embedding(model=model, input=batch, **kwargs)
            responses.append((response, cache_hit, call_log))
        
    embeddings = []
    for response, cache_hit, call_log in responses:
        embeddings.extend([d['embedding'] for d in response.data])
    return embeddings, responses


# %%
embeddings, responses = batch_embeddings(
    model="text-embedding-3-small",
    input=[
        "First string to embed",
        "Second string to embed",
        "Third string to embed",
        "Fourth string to embed",
    ],
    batch_size=2,
    verbose=False,
)

# %%
#|hide
show_doc(this_module.async_batch_embeddings)


# %%
#|export
async def async_batch_embeddings(
    model: str,
    input: list[str] = None,
    batch_size: int = 1000,
    verbose: bool = False,
    **kwargs
):
    """
    Compute embeddings for a list of input strings in batches asynchronously.

    Args:
        model (str): The embedding model to use.
        input (list[str]): List of input strings to embed.
        batch_size (int): Number of inputs per batch.
        verbose (bool): If True, display a progress bar.
        **kwargs: Additional keyword arguments passed to `async_embedding`.

    Returns:
        list: List of embedding vectors for each input string.
    """
    embedding_tasks = []
    for i in range(0, len(input), batch_size):
        batch = input[i:i + batch_size]
        embedding_tasks.append(async_embedding(model=model, input=batch, **kwargs))
    
    if verbose:
        from tqdm.asyncio import tqdm_asyncio
        responses = await tqdm_asyncio.gather(*embedding_tasks, desc="Processing embedding batches", total=len(embedding_tasks))
    else:
        responses = await asyncio.gather(*embedding_tasks)
        
    embeddings = []
    for response, _, _ in responses:
        embeddings.extend([d['embedding'] for d in response.data])
    return embeddings, responses


# %%
embeddings, responses = await async_batch_embeddings(
    model="text-embedding-3-small",
    input=[
        "First string to embed",
        "Second string to embed",
        "Third string to embed",
        "Fourth string to embed",
    ],
    batch_size=2,
    verbose=False,
)
