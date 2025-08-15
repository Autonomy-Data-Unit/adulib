# %% [markdown]
# # _utils

# %%
#|default_exp llm._utils

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
try:
    import litellm
    import inspect
    import time
    import asyncio
    import warnings
    from typing import Callable, Optional, Union
    from pathlib import Path
    from adulib.caching import get_default_cache_path
    from adulib.llm.caching import _cache_execute, _async_cache_execute, get_cache_key, is_in_cache
    from adulib.llm.call_logging import _log_call, get_cached_call_log
    from adulib.llm.rate_limits import _get_limiter, default_retry_on_exception, default_max_retries, default_retry_delay, default_timeout
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
from adulib.caching import set_default_cache_path
import adulib.llm._utils as this_module

# %%
#|hide
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')


# %%
#|exporti
class MaximumRetriesException(Exception):
    def __init__(self, retry_exceptions: list[Exception]):
        self.retry_exceptions = retry_exceptions
        self.retry_exceptions_str = "\n".join([f"{i}: ({type(e).__name__}) {e}" for i, e in enumerate(retry_exceptions)])
        super().__init__(f"Maximum retries ({len(retry_exceptions)}) reached. Exceptions:\n{self.retry_exceptions_str}")


# %%
#|exporti
def _llm_func_factory(
    func: Callable,
    func_name: str,
    func_cache_name: str,
    module_name: str,
    retrieve_log_data: Optional[Callable] = None,
    default_return_info: bool = True,
):
    func_sig = inspect.signature(func)
    def llm_func(
        *args,
        # Cache settings
        cache_enabled: bool=True,
        cache_path: Optional[Union[str, Path]]=None,
        cache_key_prefix: Optional[str]=None,
        include_model_in_cache_key: bool=True,
        return_cache_key: bool=False,
        return_info: bool=default_return_info,
        # Retry settings
        enable_retries: bool=True,
        retry_on_exceptions: Optional[list[Exception]]=None,
        retry_on_all_exceptions: bool=False,
        max_retries: Optional[int]=None,
        retry_delay: Optional[int]=None,
        **kwargs,
    ):
        if retry_on_exceptions is None: retry_on_exceptions = default_retry_on_exception
        if max_retries is None: max_retries = default_max_retries
        if retry_delay is None: retry_delay = default_retry_delay
        
        # Generate cache key
        bound = func_sig.bind(*args, **kwargs)
        func_args_and_kwargs = dict(bound.arguments)
        model = func_args_and_kwargs.pop('model') # we treat 'model' separately, as we can optionally exclude it from the cache key
        cache_key = get_cache_key(model, func_cache_name, func_args_and_kwargs, cache_key_prefix, include_model_in_cache_key)
        if return_cache_key: return cache_key
        
        if cache_path is None:
            cache_path = get_default_cache_path()
        
        # Execute with caching and retries
        success = False
        exceptions = []
        for _ in range(max_retries):
            try:
                cache_hit, result = _cache_execute(
                    cache_key=cache_key,
                    execute_func=lambda: func(*args, **kwargs),
                    cache_enabled=cache_enabled,
                    cache_path=cache_path,
                )
                success = True
                break
            except BaseException as e:
                if not enable_retries: raise e
                if not (retry_on_all_exceptions or any([isinstance(e, exc) for exc in retry_on_exceptions])): raise e
                exceptions.append(e)
                time.sleep(retry_delay)
                    
        if not success:
            raise MaximumRetriesException(exceptions)
        
        # Call logging
        if retrieve_log_data is not None:
            if not cache_hit:
                cache_args = {
                    "cache_path": cache_path,
                    "cache_key_prefix": cache_key_prefix,
                    "include_model_in_cache_key": include_model_in_cache_key,
                }
                log_data = retrieve_log_data(model, func_args_and_kwargs, result, cache_args)
                _log_call(cache_key, cache_path, model=model, **log_data)

            call_info = get_cached_call_log(cache_key, cache_path)
            if call_info is None:
                warnings.warn(f"Call log for cache key '{cache_key}' not found in cache at '{cache_path}'. This may indicate a caching issue.")
        
        if return_info:
            if retrieve_log_data is not None:
                return result, cache_hit, call_info
            else:
                return result, cache_hit
        else:
            return result
    
    llm_func.__name__ = func_name
    llm_func.__module__ = module_name
    llm_func.__qualname__ = func_name
    return llm_func


# %%
#|hide
def foo(model):
    raise litellm.RateLimitError(None, None, None)

_foo = _llm_func_factory(
    func=foo,
    func_name="foo",
    func_cache_name="foo",
    module_name="foo_module"
)

try:
    _foo(model="foo", retry_delay=0.01)
except MaximumRetriesException as e:
    print(e)


# %%
#|hide
def foo(model):
    raise ValueError("Failed!")

_foo = _llm_func_factory(
    func=foo,
    func_name="foo",
    func_cache_name="foo",
    module_name="foo_module",
    retrieve_log_data=lambda model, func_kwargs, response: { "method": "foo", "input_tokens": None, "output_tokens": None, "cost": 0 },
)

try:
    _foo(model="foo", retry_on_exceptions=[ValueError], retry_delay=0.01)
except MaximumRetriesException as e:
    print(e)


# %%
#|exporti
def _llm_async_func_factory(
    func: Callable,
    func_name: str,
    func_cache_name: str,
    module_name: str,
    retrieve_log_data: Optional[Callable] = None,
    default_return_info: bool = True,
):
    func_sig = inspect.signature(func)
    async def llm_func(
        *args,
        # Cache settings
        cache_enabled: bool=True,
        cache_path: Optional[Union[str, Path]]=None,
        cache_key_prefix: Optional[str]=None,
        include_model_in_cache_key: bool=True,
        return_cache_key: bool=False,
        return_info: bool=default_return_info,
        # Retry settings
        enable_retries: bool=True,
        retry_on_exceptions: Optional[list[Exception]]=None,
        retry_on_all_exceptions: bool=False,
        max_retries: Optional[int]=None,
        retry_delay: Optional[int]=None,
        timeout: Optional[int]=None,
        **kwargs,
    ):
        if retry_on_exceptions is None: retry_on_exceptions = default_retry_on_exception
        if max_retries is None: max_retries = default_max_retries
        if retry_delay is None: retry_delay = default_retry_delay
        if timeout is None: timeout = default_timeout
        
        # Generate cache key
        bound = func_sig.bind(*args, **kwargs)
        func_args_and_kwargs = dict(bound.arguments)
        model = func_args_and_kwargs.pop('model') # we treat 'model' separately, as we can optionally exclude it from the cache key
        cache_key = get_cache_key(model, func_cache_name, func_args_and_kwargs, cache_key_prefix, include_model_in_cache_key)
        if return_cache_key: return cache_key
        
        if cache_path is None:
            cache_path = get_default_cache_path()
        
        # Rate limiting
        key_in_cache = is_in_cache(cache_key, cache=cache_path)
        if not key_in_cache:
            api_key = kwargs.get("api_key", None)
            await _get_limiter(model, api_key).wait()
        
        # Execute with caching and retries
        success = False
        exceptions = []
        async def run_with_timeout():
            return await asyncio.wait_for(func(*args, **kwargs), timeout)
        for _ in range(max_retries):
            try:                
                cache_hit, result = await _async_cache_execute(
                    cache_key=cache_key,
                    execute_func=run_with_timeout if timeout is not None else lambda: func(*args, **kwargs),
                    cache_enabled=cache_enabled,
                    cache_path=cache_path,
                )
                success = True
                break
            except BaseException as e:
                if not enable_retries: raise e
                if not (retry_on_all_exceptions or any([isinstance(e, exc) for exc in retry_on_exceptions])): raise e
                exceptions.append(e)
                await asyncio.sleep(retry_delay)
                    
        if not success:
            raise MaximumRetriesException(exceptions)
        
        # Call logging
        if retrieve_log_data is not None:
            if not cache_hit:
                cache_args = {
                    "cache_path": cache_path,
                    "cache_key_prefix": cache_key_prefix,
                    "include_model_in_cache_key": include_model_in_cache_key,
                }
                log_data = retrieve_log_data(model, func_args_and_kwargs, result, cache_args)
                _log_call(cache_key, cache_path, model=model, **log_data)

            call_info = get_cached_call_log(cache_key, cache_path)
            if call_info is None:
                warnings.warn(f"Call log for cache key '{cache_key}' not found in cache at '{cache_path}'. This may indicate a caching issue.")
        
        if return_info:
            if retrieve_log_data is not None:
                return result, cache_hit, call_info
            else:
                return result, cache_hit
        else:
            return result
    
    llm_func.__name__ = func_name
    llm_func.__module__ = module_name
    llm_func.__qualname__ = func_name
    return llm_func


# %%
#|hide
async def foo(model):
    raise litellm.RateLimitError(None, None, None)

_foo = _llm_async_func_factory(
    func=foo,
    func_name="foo",
    func_cache_name="foo",
    module_name="foo_module",
)

try:
    await _foo(model="foo", retry_delay=0.01)
except MaximumRetriesException as e:
    print(e)


# %%
#|hide
async def bar(model):
    await asyncio.sleep(10)

_foo = _llm_async_func_factory(
    func=bar,
    func_name="bar",
    func_cache_name="bar",
    module_name="bar_module",
)

try:
    await _foo(model="bar", retry_delay=0.01, timeout=0.01)
except MaximumRetriesException as e:
    print(e)
