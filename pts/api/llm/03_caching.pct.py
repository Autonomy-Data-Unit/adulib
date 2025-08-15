# %% [markdown]
# # caching

# %%
#|default_exp llm.caching

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
try:
    from pathlib import Path
    from typing import Dict, Union, Callable, Coroutine
    from adulib.caching import get_cache, clear_cache_key, is_in_cache, get_default_cache
    from diskcache import ENOVAL
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
from adulib.caching import set_default_cache_path
import adulib.llm.caching as this_module

# %%
#|hide
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')


# %%
#|export
def get_cache_key(
    model: str, func_name, content: any, key_prefix: Union[str, None]=None, include_model_in_cache_key: bool=True
) -> tuple:
    return ('adulib.llm', func_name, key_prefix, model if include_model_in_cache_key else '', content)


# %%
#|exporti
def _cache_execute(
    cache_key: tuple,
    execute_func: Callable,
    cache_enabled: bool=True,
    cache_path: Union[str, Path, None]=None,
):
    if not cache_enabled: return execute_func()
    cache = get_cache(cache_path) if cache_path is not None else get_default_cache()
    result = cache.get(cache_key, default=ENOVAL, retry=True)
    retrieved_from_cache = True
    if result is ENOVAL:
        result = execute_func()
        cache.set(cache_key, result)
        retrieved_from_cache = False
    return retrieved_from_cache, result


# %%
#|exporti
async def _async_cache_execute(
    cache_key: tuple,
    execute_func: Callable,
    cache_enabled: bool=True,
    cache_path: Union[str, Path, None]=None,
):
    if not cache_enabled: return execute_func()
    cache = get_cache(cache_path) if cache_path is not None else get_default_cache()
    result = cache.get(cache_key, default=ENOVAL, retry=True)
    retrieved_from_cache = True
    if result is ENOVAL:
        result = await execute_func()
        cache.set(cache_key, result)
        retrieved_from_cache = False
    return retrieved_from_cache, result
