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
except ImportError as e:
    raise ImportError(f"Install adulib[{__name__.split('.')[-1]}] to use this API.") from e

from adulib.utils import check_mutual_exclusivity

# %%
import time
import adulib.caching as this_module

# %%
show_doc(this_module.memoize)

# %%
#|exporti
__caches = {}
__memoized_function_names = set()
__tmp_cache = None

def _get_cache(cache_path=None, cache=None, temp=False):
    global __tmp_cache
    if not check_mutual_exclusivity(cache_path, cache, temp):
        raise ValueError("Either cache_path or cache is provided, or temp must be set to True.")
    
    if cache is None:
        if cache_path is None:
            if __tmp_cache is None: __tmp_cache = diskcache.Cache()
            cache = __tmp_cache
        else:
            cache_path = Path(cache_path).as_posix()
            if cache_path in __caches:
                cache = __caches[cache_path]
            else:
                cache = diskcache.Cache(cache_path)
                __caches[cache_path] = cache
                
    return cache


# %%
#|export
def memoize(cache_path=None,
            cache=None,
            temp=False,
            typed=True,
            expire=None,
            tag=None,
            ):
    """
    Memoization decorator to cache function results.

    This decorator can be used to cache the results of a function call
    to improve performance by avoiding repeated evaluations of the same
    function with the same arguments. The cache can be specified by
    providing a `cache_path`, an existing `cache` object, or by setting
    `temp` to True to use a temporary cache.

    Parameters:
    - cache_path (str, optional): Path to the cache directory. If not
      provided, a temporary cache will be used if `temp` is True.
    - cache (diskcache.Cache, optional): An existing cache object to use.
    - temp (bool, optional): If True, use a temporary cache. Defaults to False.
    - typed (bool, optional): If True, cache function arguments of different
      types separately. Defaults to True.
    - expire (int, optional): Time in seconds for cache expiration. If None,
      cache entries do not expire.
    - tag (str, optional): A tag to associate with the cache entries.

    Returns:
    - decorator (function): A decorator that wraps the function with
      memoization logic.
    """

    cache = _get_cache(cache_path, cache, temp)
                
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
