# %% [markdown]
# # adulib.caching
#
# Utilities for working with notebooks.

# %%
#|default_exp caching

# %%
#|hide
import nblite; from nbdev.showdoc import show_doc; nblite.nbl_export()

# %%
#|export
try:
    import diskcache
    from pathlib import Path
    from diskcache.core import ENOVAL, args_to_key, full_name
    import functools as ft
    import asyncio
    from typing import Union
except ImportError as e:
    raise ImportError(f"Install adulib[{__name__.split('.')[-1]}] to use this API.") from e

from adulib.utils import check_mutual_exclusivity

# %%
import time
import adulib.caching as this_module

# %%
#|exporti
_caches = {}
_default_cache = None
_default_cache_path = None

# %%
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
show_doc(this_module.get_default_cache_path)


# %%
#|export
def get_default_cache_path() -> Path|None:
    """
    Set the path for the temporary cache.
    """
    return _default_cache_path


# %%
show_doc(this_module.create_cache)


# %%
#|export
def create_cache(cache_path:Union[Path,None]=None, temp:bool=False):
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
        if _default_cache is None: _default_cache = create_cache(_default_cache_path)
        cache = _default_cache
    else:
        cache_path = Path(cache_path).as_posix()
        if cache_path in _caches:
            cache = _caches[cache_path]
        else:
            cache = create_cache(cache_path)
            _caches[cache_path] = cache


# %%
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
):
    """
    Memoization decorator to cache function results.

    This decorator caches the results of a function call to enhance performance
    by avoiding repeated evaluations of the same function with identical arguments.
    The cache can be specified by providing an existing `cache` object or by using
    a temporary cache if no cache is provided.

    Parameters:
    - cache (Union[Path, diskcache.Cache, None], optional): An existing cache object
        or a path to the cache directory. If None, a temporary cache is used.
    - typed (bool, optional): If True, cache function arguments of different types
        separately. Defaults to True.
    - expire (int, optional): Time in seconds for cache expiration. If None, cache
        entries do not expire.
    - tag (str, optional): A tag to associate with the cache entries.

    Returns:
    - function: A decorator that wraps the function with memoization logic.
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
        cache = create_cache(temp=True)
                            
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
                return result
            return wrapper
        else:
            memoized_f = cache.memoize(expire=expire, tag=tag, typed=typed)(func)
            return memoized_f
                                
    return decorator


# %%
@memoize(temp=True)
def foo():
    time.sleep(1)
    return "bar"

foo() # Takes 1 second
foo() # Is retrieved from cache and returns immediately


# %%
@memoize(temp=True)
async def async_foo():
    time.sleep(1)
    return "bar"

await async_foo() # Takes 1 second
await async_foo() # Is retrieved from cache and returns immediately
