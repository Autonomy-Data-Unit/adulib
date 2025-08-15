# %% [markdown]
# # call_logging

# %%
#|default_exp llm.call_logging

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
try:
    from datetime import datetime, timezone
    from pydantic import BaseModel, Field
    from typing import List, Optional
    from pathlib import Path
    import json
    from adulib.llm.base import available_models
    from adulib.caching import get_cache
    import uuid
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
import adulib.llm.call_logging as this_module


# %%
#|export
class CallLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    method: str
    model: str
    cost: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

_call_logs: List[CallLog] = []
_call_log_save_path: Optional[Path] = None


# %%
#|export
def set_call_log_save_path(path: Path):
    global _call_log_save_path, _call_logs
    _call_log_save_path = path
    if Path(path).suffix != '.jsonl':
        raise ValueError(f"Path must have a .jsonl extension")
    save_call_log(_call_log_save_path, combine_with_existing=True)
    _call_logs = load_call_log_file(path)


# %%
#|exporti
def _log_call(cache_key, cache_path, **log_kwargs):
    log_kwargs = {**log_kwargs, 'cache_key': cache_key}
    call_log = CallLog(**log_kwargs)
    _call_logs.append(call_log)
    if _call_log_save_path is not None:
        with open(_call_log_save_path, 'a') as f:
            f.write('\n' + call_log.model_dump_json())
    
    cache = get_cache(cache_path)
    cache[('call_log', cache_key)] = call_log.model_dump()


# %%
#|export
def get_cached_call_log(cache_key, cache_path):
    cache = get_cache(cache_path)
    return cache.get(('call_log', cache_key), None)


# %%
#|export
def get_call_logs(model: Optional[str]=None) -> List[CallLog]:
    _filtered_logs = _call_logs
    if model is not None:
        if model not in available_models:
            raise ValueError(f"Model '{model}' not found in available models")
        _filtered_logs = [c for c in _filtered_logs if c.model == model]
    return _filtered_logs


# %%
#|export
def get_total_costs(model: Optional[str]=None) -> float:
    _filtered_logs = get_call_logs(model)
    return sum([c.cost for c in _filtered_logs])


# %%
#|export
def get_total_input_tokens(model: Optional[str]=None) -> int:
    _filtered_logs = get_call_logs(model)
    return sum([c.input_tokens for c in _filtered_logs if c.input_tokens is not None])

def get_total_output_tokens(model: Optional[str]=None) -> int:
    _filtered_logs = get_call_logs(model)
    return sum([c.output_tokens for c in _filtered_logs if c.output_tokens is not None])

def get_total_tokens(model: Optional[str]=None) -> int:
    return get_total_input_tokens(model) + get_total_output_tokens(model)


# %%
#|export
def save_call_log(path: Path, combine_with_existing: bool = True):
    if combine_with_existing:
        _logs_on_hd = load_call_log_file(path) if Path(path).exists() else []
        _memory_call_log_ids = set([l.id for l in _call_logs])
        _logs_to_save = _call_logs + [l for l in _logs_on_hd if l.id not in _memory_call_log_ids]
    else:
        _logs_to_save = _call_logs
    
    with open(path, 'w') as f:
        for log in _logs_to_save:
            f.write(log.model_dump_json() + '\n')


# %%
#|export
def load_call_log_file(path: Optional[Path] = None) -> List[CallLog]:
    if path is None:
        path = _call_log_save_path
    if _call_log_save_path is None:
        raise ValueError("Call log save path is not set")
    with open(path, 'r') as f:
        return [CallLog(**json.loads(line)) for line in f if line.strip()]
