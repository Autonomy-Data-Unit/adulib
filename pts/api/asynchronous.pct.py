# %% [markdown]
# # adulib.asynchronous
#
# Utilities for async programming.

# %%
#|default_exp asynchronous

# %%
#| hide
from nbdev.showdoc impor show_doc

# %%
#| hide
import nbdev; nbdev.nbdev_export()

# %%
#|export
import asyncio

# %%
import adulib.asynchronous


# %%
#|export
def is_in_event_loop():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False
