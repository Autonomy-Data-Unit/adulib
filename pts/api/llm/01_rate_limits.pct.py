# %% [markdown]
# # rate_limits

# %%
#|default_exp llm.rate_limits

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
try:
    import litellm
    from asynciolimiter import Limiter
    from typing import Dict, Literal, Union
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
import adulib.llm.rate_limits as this_module

# %%
#|export
default_rpm = 1000 # requests per minute
default_retry_on_exception = [
    litellm.RateLimitError,
]
default_max_retries = 5
default_retry_delay = 10 # seconds

# %%
#|exporti
_request_rate_limiters: Dict[str, Limiter] = {}


# %%
#|exporti
def _convert_to_per_minute(rate: float, unit: Literal['per-second', 'per-minute', 'per-hour'] = 'per-minute') -> float:
    if unit == 'per-second':
        return rate * 60
    elif unit == 'per-hour':
        return rate / 60
    else:
        return rate


# %%
#|export
def set_default_request_rate_limit(
    request_rate: float, request_rate_unit: Literal['per-second', 'per-minute', 'per-hour'] = 'per-minute'
):
    global default_rpm
    default_rpm = _convert_to_per_minute(request_rate, request_rate_unit)
    return default_rpm


# %%
#|exporti
def _get_limiter(model: str, api_key: Union[str, None]=None) -> Limiter:
    key = f"{model}-{api_key}" if api_key is not None else model
    if key not in _request_rate_limiters:
        _request_rate_limiters[key] = Limiter(default_rpm / 60)
    return _request_rate_limiters.get(key, None)


# %%
#|export
def set_request_rate_limit(
    model: str, api_key: str|None, request_rate: float, request_rate_unit: Literal['per-second', 'per-minute', 'per-hour'] = 'per-minute'
):
    limiter = _get_limiter(model, api_key)
    if limiter is not None:
        limiter.breach() # Release any pending requests
    key = f"{model}-{api_key}" if api_key is not None else model
    rpm = _convert_to_per_minute(request_rate, request_rate_unit)
    _request_rate_limiters[key] = Limiter(rpm / 60)

# %% [markdown]
# You may consult the rate limits to match those given in the developer consoles of the APIs you use. For example:
#
# - [Anthropic console](https://console.anthropic.com/settings/limits)
# - [OpenAI console](https://platform.openai.com/settings/organization/limits)
# - [Google console](https://ai.google.dev/gemini-api/docs/rate-limits?authuser=1#tier-1)
# - DeepSeek currently does not impose any rate limits
