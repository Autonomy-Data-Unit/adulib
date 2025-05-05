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
    import functools
    from typing import Callable, Optional, Union
    from pathlib import Path
    from adulib.llm.caching import _cache_execute, _async_cache_execute, get_cache_key, is_in_cache
    from adulib.llm.call_logging import _log_call
    from adulib.llm.rate_limits import _get_limiter
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
import adulib.llm._utils as this_module


# %%
def get_cache_key(
    model: str, method_name, content: any, cache_key_prepend: Union[str, None]=None, include_model_in_cache_key: bool=True
) -> tuple:
    return ('adulib.llm', method_name, cache_key_prepend, model if include_model_in_cache_key else '', content)


# %%
#|exporti
def _llm_func_factory(
    func: Callable,
    func_name: str,
    func_cache_name: str,
    retrieve_log_data: Optional[Callable] = None,
):
    func_sig = inspect.signature(func)
    def llm_func(
        *args,
        cache_enabled: bool=True,
        cache_path: Optional[Union[str, Path]]=None,
        cache_key_prefix: Optional[str]=None,
        include_model_in_cache_key: bool=True,
        return_cache_key: bool=False,
        **kwargs,
    ):
        # Generate cache key
        bound = func_sig.bind(*args, **kwargs)
        func_args_and_kwargs = dict(bound.arguments)
        model = func_args_and_kwargs.pop('model') # we treat 'model' separately, as we can optionally exclude it from the cache key
        cache_key = get_cache_key(model, func_cache_name, func_args_and_kwargs, cache_key_prefix, include_model_in_cache_key)
        if return_cache_key: return cache_key
        
        # Caching
        retrieved_from_cache, result = _cache_execute(
            cache_key=cache_key,
            execute_func=lambda: func(*args, **kwargs),
            cache_enabled=cache_enabled,
            cache_path=cache_path,
        )
        
        # Call logging
        if retrieve_log_data is not None:
            if not retrieved_from_cache:
                log_data = retrieve_log_data(model, func_args_and_kwargs, result)
                _log_call( model=model, **log_data)
        
        return result
    
    llm_func.__name__ = func_name
    return llm_func


# %%
#|exporti
def _llm_async_func_factory(
    func: Callable,
    func_name: str,
    func_cache_name: str,
    retrieve_log_data: Optional[Callable] = None,
):
    func_sig = inspect.signature(func)
    async def llm_func(
        *args,
        cache_enabled: bool=True,
        cache_path: Optional[Union[str, Path]]=None,
        cache_key_prefix: Optional[str]=None,
        include_model_in_cache_key: bool=True,
        return_cache_key: bool=False,
        **kwargs,
    ):
        # Generate cache key
        bound = func_sig.bind(*args, **kwargs)
        func_args_and_kwargs = dict(bound.arguments)
        model = func_args_and_kwargs.pop('model') # we treat 'model' separately, as we can optionally exclude it from the cache key
        cache_key = get_cache_key(model, func_cache_name, func_args_and_kwargs, cache_key_prefix, include_model_in_cache_key)
        if return_cache_key: return cache_key
        
        # Rate limiting
        key_in_cache = is_in_cache(cache_key)
        if not key_in_cache:
            api_key = kwargs.get("api_key", None)
            await _get_limiter(model, api_key).wait()
        
        # Caching
        retrieved_from_cache, result = await _async_cache_execute(
            cache_key=cache_key,
            execute_func=lambda: func(*args, **kwargs),
            cache_enabled=cache_enabled,
            cache_path=cache_path,
        )
        
        # Call logging
        if retrieve_log_data is not None:
            if not retrieved_from_cache:
                log_data = retrieve_log_data(model, func_args_and_kwargs, result)
                _log_call(model=model, **log_data)
        
        return result
    
    llm_func.__name__ = func_name
    return llm_func
