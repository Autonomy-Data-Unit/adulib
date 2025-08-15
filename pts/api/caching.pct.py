# %% [markdown]
# # caching
#
# Utilities for working with notebooks.

# %%
#|default_exp caching

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
import diskcache
from pathlib import Path
from diskcache.core import ENOVAL, args_to_key, full_name
import functools as ft
import asyncio
from typing import Union
from adulib.utils import check_mutual_exclusivity

# %%
#|hide
import time
import adulib.caching as this_module

# %%
#|exporti
_caches = {}
_default_cache = None
_default_cache_path = None

# %%
#|hide
show_doc(this_module.set_default_cache_path)


# %%
#|export
def set_default_cache_path(cache_path:Path):
    """
    Set the path for the temporary cache.
    """
    global _default_cache_path
    _default_cache_path = cache_path


# %%
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')

# %%
#|hide
show_doc(this_module.get_default_cache_path)


# %%
#|export
def get_default_cache_path() -> Path|None:
    """
    Set the path for the temporary cache.
    """
    return _default_cache_path


# %%
#|hide
show_doc(this_module._create_cache)


# %%
#|exporti
def _create_cache(cache_path:Union[Path,None]=None, temp:bool=False):
    """
    Creates a new cache with the right policies. This ensures that no data is lost as the cache grows.
    """
    if temp and cache_path is not None:
        raise ValueError("'temp' cannot be set to True if a 'cache_path' is provided.")

    if cache_path is None and not temp:
        if _default_cache_path is None:
            raise ValueError("The default cache path is not set. Please set it using `set_default_cache_path`.")
        cache_path = _default_cache_path
    
    return diskcache.Cache(cache_path, eviction_policy="none", size_limit=2**40)


# %%
show_doc(this_module.get_default_cache)


# %%
#|export
def get_default_cache():
    """
    Retrieve the default cache.
    """
    global _default_cache
    if _default_cache_path is None:
        raise ValueError("The default cache path is not set. Please set it using `set_default_cache_path`.")
    if _default_cache is None:
        _default_cache = _create_cache(_default_cache_path)
    return _default_cache


# %%
#|hide
show_doc(this_module.get_cache)


# %%
#|export
def get_cache(cache_path:Union[Path,None]=None):
    """
    Retrieve a cache instance for the given path. If no path is provided, 
    the default cache is used. If the cache does not exist, it is created 
    using the specified cache path or the default cache path.
    """
    if cache_path is None:
        global _default_cache
        if _default_cache is None: _default_cache = _create_cache()
        cache = _default_cache
    else:
        cache_path = Path(cache_path).as_posix()
        if cache_path in _caches:
            cache = _caches[cache_path]
        else:
            cache = _create_cache(cache_path)
            _caches[cache_path] = cache
    return cache


# %%
#|hide
show_doc(this_module.clear_cache_key)


# %%
#|export
def clear_cache_key(cache_key, cache:Union[Path,diskcache.Cache,None]=None, allow_non_existent:bool=False):
    if cache is None:
        cache = get_default_cache()
    elif isinstance(cache, diskcache.Cache):
        pass # do nothing
    else:
        cache_path = cache
        cache = get_cache(cache_path)
    if allow_non_existent and cache_key not in cache: return
    del cache[cache_key]


# %%
#|hide
show_doc(this_module.is_in_cache)


# %%
#|export
def is_in_cache(key: tuple, cache:Union[Path,diskcache.Cache,None]=None):
    if cache is None:
        cache = get_default_cache()
    elif isinstance(cache, diskcache.Cache):
        pass # do nothing
    else:
        cache_path = cache
        cache = get_cache(cache_path)
    return cache.get(key, default=ENOVAL) is not ENOVAL


# %%
#|hide
show_doc(this_module.memoize)

# %%
#|exporti
__memoized_function_names = set()


# %%
#|export
def memoize(cache:Union[Path,diskcache.Cache,None]=None,
            temp=False,
            typed=True,
            expire=None,
            tag=None,
            return_cache_key=False,
):
    """
    Decorator for memoizing function results to improve performance.

    This decorator stores the results of function calls, allowing subsequent
    calls with the same arguments to retrieve the result from the cache instead
    of recomputing it. You can specify a cache object or use a temporary cache
    if none is provided.

    Parameters:
    - cache (Union[Path, diskcache.Cache, None], optional): A cache object or a
      path to the cache directory. Defaults to a temporary cache if None.
    - temp (bool, optional): If True, use a temporary cache. Cannot be True if
      a cache is provided. Defaults to False.
    - typed (bool, optional): If True, cache function arguments of different
      types separately. Defaults to True.
    - expire (int, optional): Cache expiration time in seconds. If None, cache
      entries do not expire.
    - tag (str, optional): A tag to associate with cache entries.
    - return_cache_key (bool, optional): If True, return the cache key along
      with the result, in the order `(cache_key, result)`. Defaults to False.

    Returns:
    - function: A decorator that applies memoization to the target function.
    """

    if temp and cache is not None:
        raise ValueError("'temp' cannot be set to True if a cache is provided.")
    
    if not temp:
        if cache is None:
            cache = get_cache()
        elif isinstance(cache, diskcache.Cache):
            pass # do nothing
        else:
            cache_path = cache
            cache = get_cache(cache_path)
    else:
        cache = _create_cache(temp=True)
                            
    def decorator(func):
        func_name = full_name(func)
        if func_name in __memoized_function_names:
            print(f"Warning: A function with the name '{func_name}' is already memoized.")
        __memoized_function_names.add(func_name)
        if asyncio.iscoroutinefunction(func):
            @ft.wraps(func)
            async def wrapper(*args, **kwargs):
                key = args_to_key((func_name,), args, kwargs, typed, ())
                result = cache.get(key, default=ENOVAL, retry=True)
                if result is ENOVAL:
                    result = await func(*args, **kwargs)
                    if expire is None or expire > 0:
                        cache.set(key, result, expire, tag=tag, retry=True)
                if return_cache_key:
                    return key, result
                return result
        else:
            def wrapper(*args, **kwargs):
                key = args_to_key((func_name,), args, kwargs, typed, ())
                result = cache.get(key, default=ENOVAL, retry=True)
                if result is ENOVAL:
                    result = func(*args, **kwargs)
                    if expire is None or expire > 0:
                        cache.set(key, result, expire, tag=tag, retry=True)
                if return_cache_key:
                    return key, result
                return result
        return wrapper
                                
    return decorator


# %%
@memoize(temp=True)
def foo():
    time.sleep(1)
    return "bar"

foo() # Takes 1 second
foo() # Is retrieved from cache and returns immediately


# %%
@memoize(return_cache_key=True)
async def async_foo():
    time.sleep(1)
    return "bar"

await async_foo() # Takes 1 second
cache_key, result = await async_foo() # Is retrieved from cache and returns immediately
clear_cache_key(cache_key) # Clears the cache key
await async_foo(); # This should again take 1 second
