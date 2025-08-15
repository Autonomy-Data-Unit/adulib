# %% [markdown]
# # tokens

# %%
#|default_exp llm.tokens

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
try:
    import litellm
    from adulib.llm._utils import _llm_func_factory
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
from adulib.caching import set_default_cache_path
from adulib.llm.caching import is_in_cache, clear_cache_key
import adulib.llm.tokens as this_module

# %%
#|hide
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')

# %%
#|echo: false
show_doc(this_module.token_counter)

# %%
#|export
token_counter = _llm_func_factory(
    func=litellm.token_counter,
    func_name="token_counter",
    func_cache_name="token_counter",
    module_name=__name__,
    cache_key_content_args=['messages', 'text'],
    default_return_info=False,
)

# %%
token_counter(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

# %% [markdown]
# If we set `return_cache_key=True`, the function is not executed and only the cache key is returned instead.

# %%
# This will not execute the function, but only return the cache key.
cache_key = token_counter(
    model="gpt-4o",
    text="Hello, how are you?",
    return_cache_key=True,
)

clear_cache_key(cache_key, allow_non_existent=True)
assert not is_in_cache(cache_key)

# This will cache the result.
num_tokens, cache_hit = token_counter(
    model="gpt-4o",
    text="Hello, how are you?",
    return_info=True
)
assert not cache_hit

num_tokens, cache_hit = token_counter(
    model="gpt-4o",
    text="Hello, how are you?",
    return_info=True
)
assert cache_hit

assert is_in_cache(cache_key)
clear_cache_key(cache_key)
