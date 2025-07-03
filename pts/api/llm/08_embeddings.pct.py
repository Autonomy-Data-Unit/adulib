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
response = embedding(
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
response = await async_embedding(
    model="text-embedding-3-small",
    input=[
        "First string to embed",
        "Second string to embed",
    ],
)
response.data[1]['embedding'][:10]
