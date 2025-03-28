# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/api/utils.ipynb.

# %% auto 0
__all__ = ['check_mutual_exclusivity']

# %% ../nbs/api/utils.ipynb 4
def check_mutual_exclusivity(*args, check_falsy=True):
    """
    Check if only one of the arguments is falsy (or truthy, if check_falsy is False).
    """
    if check_falsy:
        return sum(bool(x) for x in args) == 1
    else:
        return sum(bool(x) for x in args) == 1
