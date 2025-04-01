# %% [markdown]
# # adulib.utils
#
# General utility functions.

# %%
#|default_exp utils

# %%
#|hide
import nblite; from nbdev.showdoc import show_doc; nblite.nbl_export()


# %%
#|export
def check_mutual_exclusivity(*args, check_falsy=True):
    """
    Check if only one of the arguments is falsy (or truthy, if check_falsy is False).
    """
    if check_falsy:
        return sum(bool(x) for x in args) == 1
    else:
        return sum(bool(x) for x in args) == 1

# %%
