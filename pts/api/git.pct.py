# %% [markdown]
# # git

# %%
#|default_exp git

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.git as this_module

# %%
#|export
from pathlib import Path
import os

# %%
#|hide
show_doc(this_module.find_root_repo_path)


# %%
#|export
def find_root_repo_path(path=None):
    current_path = Path(path or '.').expanduser().resolve()
    home_path = Path.home()
    
    while current_path != home_path:
        if (current_path / '.git').exists():
            return str(current_path)
        parent_path = current_path.parent
        if parent_path == current_path:  # Reached the root directory
            break
        current_path = parent_path
    
    return None


# %%
root_repo_path = find_root_repo_path()
