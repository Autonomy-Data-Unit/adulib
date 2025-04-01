# %% [markdown]
# # adulib.caching
#
# Utilities for working with notebooks.

# %%
#|default_exp caching

# %%
#| hide
from nbdev.showdoc import show_doc

# %%
#| hide
import nbdev; nbdev.nbdev_export()

# %%
#|export
try:
    import diskcache
    from pathlib import Path
except ImportError as e:
    raise ImportError(f"Install adulib[{__name__.split('.')[-1]}] to use this API.") from e

from adulib.utils import check_mutual_exclusivity

# %%
#|export
cache = diskcache.Cache()

cache.memoize

# %%
#|exporti
__caches = {}
__TEMP_CACHE = 0


# %%
#|export
def memoize(cache_path=None,
            cache=None,
            temp=False,
            typed=True,
            expire=None,
            tag=None,
            ):
    
    if not check_mutual_exclusivity(cache_path, cache, temp):
        raise ValueError("One - and only one - of cache_path, cache, and temp can be provided")
    
    if cache is None:
        if cache_path is None:
            if __TEMP_CACHE in __caches:
                cache = __caches[__TEMP_CACHE]
            else:
                cache = diskcache.Cache()
                __caches[__TEMP_CACHE] = cache
        else:
            cache_path = Path(cache_path).as_posix()
            if cache_path in __caches:
                cache = __caches[cache_path]
            else:
                cache = diskcache.Cache(cache_path)
                __caches[cache_path] = cache
                
    def decorator(f):
        
        memoized_f = cache.memoize(expire=expire, tag=tag, typed=typed)(f)
        return memoized_f
    
    return decorator


# %%
import asyncio, time


# %%
@memoize(temp=True)
def foo():
    time.sleep(1)
    return "bar"

foo() # Takes 1 second
foo()


# %%
def async_memoize(
    cache, name=None, typed=False, expire=None, tag=None, ignore=()
):
    """Memoizing cache decorator.

    Decorator to wrap callable with memoizing function using cache.
    Repeated calls with the same arguments will lookup result in cache and
    avoid function evaluation.

    If name is set to None (default), the callable name will be determined
    automatically.

    When expire is set to zero, function results will not be set in the
    cache. Cache lookups still occur, however. Read
    :doc:`case-study-landing-page-caching` for example usage.

    If typed is set to True, function arguments of different types will be
    cached separately. For example, f(3) and f(3.0) will be treated as
    distinct calls with distinct results.

    The original underlying function is accessible through the __wrapped__
    attribute. This is useful for introspection, for bypassing the cache,
    or for rewrapping the function with a different cache.

    >>> from diskcache import Cache
    >>> cache = Cache()
    >>> @cache.memoize(expire=1, tag='fib')
    ... def fibonacci(number):
    ...     if number == 0:
    ...         return 0
    ...     elif number == 1:
    ...         return 1
    ...     else:
    ...         return fibonacci(number - 1) + fibonacci(number - 2)
    >>> print(fibonacci(100))
    354224848179261915075

    An additional `__cache_key__` attribute can be used to generate the
    cache key used for the given arguments.

    >>> key = fibonacci.__cache_key__(100)
    >>> print(cache[key])
    354224848179261915075

    Remember to call memoize when decorating a callable. If you forget,
    then a TypeError will occur. Note the lack of parenthenses after
    memoize below:

    >>> @cache.memoize
    ... def test():
    ...     pass
    Traceback (most recent call last):
        ...
    TypeError: name cannot be callable

    :param cache: cache to store callable arguments and return values
    :param str name: name given for callable (default None, automatic)
    :param bool typed: cache different types separately (default False)
    :param float expire: seconds until arguments expire
        (default None, no expiry)
    :param str tag: text to associate with arguments (default None)
    :param set ignore: positional or keyword args to ignore (default ())
    :return: callable decorator

    """
    # Caution: Nearly identical code exists in DjangoCache.memoize
    if callable(name):
        raise TypeError('name cannot be callable')

    def decorator(func):
        """Decorator created by memoize() for callable `func`."""
        base = (full_name(func),) if name is None else (name,)

        @ft.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper for callable to cache arguments and return values."""
            key = wrapper.__cache_key__(*args, **kwargs)
            result = self.get(key, default=ENOVAL, retry=True)

            if result is ENOVAL:
                result = func(*args, **kwargs)
                if expire is None or expire > 0:
                    self.set(key, result, expire, tag=tag, retry=True)

            return result

        def __cache_key__(*args, **kwargs):
            """Make key for cache given function arguments."""
            return args_to_key(base, args, kwargs, typed, ignore)

        wrapper.__cache_key__ = __cache_key__
        return wrapper

    return decorator


# %%
@memoize(temp=True)
async def foo2():
    time.sleep(1)
    return "bar"

await foo2()
