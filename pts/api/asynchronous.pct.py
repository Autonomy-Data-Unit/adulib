# %% [markdown]
# # asynchronous
#
# Utilities for async programming.

# %%
#|default_exp asynchronous

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
import asyncio
from tqdm.asyncio import tqdm_asyncio
from typing import Callable, Tuple, Any, Dict, Iterable, Optional

# %%
import adulib.asynchronous as this_module

# %%
#|hide
show_doc(this_module.is_in_event_loop)


# %%
#|export
def is_in_event_loop():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


# %%
#|hide
show_doc(this_module.batch_executor)


# %%
#|export
async def batch_executor(
    func: Callable,
    constant_kwargs: Dict[str, Any] = {},
    batch_args: Optional[Iterable[Tuple[Any, ...]]] = None,
    batch_kwargs: Optional[Iterable[Dict[str, Any]]] = None,
    concurrency_limit: Optional[int] = None,
    verbose: bool = True,
    progress_bar_desc: str = "Processing",
):
    """
    Executes a batch of asynchronous tasks.

    Parameters:
    - func (Callable): The asynchronous function to execute for each batch.
    - constant_kwargs (Dict[str, Any], optional): Constant keyword arguments to pass to each function call.
    - batch_args (Optional[Iterable[Tuple[Any, ...]]], optional): Iterable of argument tuples for each function call.
    - batch_kwargs (Optional[Iterable[Dict[str, Any]]], optional): Iterable of keyword argument dictionaries for each function call.
    - concurrency_limit (Optional[int], optional): Maximum number of concurrent tasks. If None, no limit is applied.
    - verbose (bool, optional): If True, displays a progress bar. Default is True.
    - progress_bar_desc (str, optional): Description for the progress bar. Default is "Processing".

    Returns:
    - List of results from the executed tasks.

    Raises:
    - ValueError: If both 'batch_args' and 'batch_kwargs' are empty or if their lengths do not match.
    """
    if not batch_args and not batch_kwargs:
        raise ValueError("At least one of 'batch_args' or 'batch_kwargs' must be non-empty.")
    
    if batch_args is None:
        batch_args = [() for _ in range(len(batch_kwargs))]
    elif batch_kwargs is None:
        batch_kwargs = [{} for _ in range(len(batch_args))]
    
    if len(batch_args) != len(batch_kwargs):
        raise ValueError("'batch_args' and 'batch_kwargs' must have the same length.")
    
    n_tasks = len(batch_args)
    semaphore = asyncio.Semaphore(concurrency_limit or n_tasks)
    
    async def execute_func(*args, **kwargs):
        async with semaphore:
            return await func(*args, **kwargs)
        
    kwargs_list = [ {**constant_kwargs, **kwargs} for kwargs in batch_kwargs ]
    tasks = [execute_func(*args, **kwargs) for args, kwargs in zip(batch_args, kwargs_list)]
    
    if verbose:
        results = await tqdm_asyncio.gather(*tasks, desc=progress_bar_desc)
    else:
        results = await asyncio.gather(*tasks)
    return results


# %%
async def sample_function(x, y, z):
    await asyncio.sleep(0.1)
    return z*(x + y)

constant_kwargs = {'z': 10}
batch_args = [(1,), (3,), (5,)]
batch_kwargs = [{'y': 2}, {'y': 4}, {'y': 6}]

results = await batch_executor(
    func=sample_function,
    constant_kwargs=constant_kwargs,
    batch_args=batch_args,
    batch_kwargs=batch_kwargs,
    concurrency_limit=2,
)

print("Results:", results)
