# %% [markdown]
# # cli

# %%
#|default_exp cli

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.cli as this_module

# %%
#|export
from typing import List, Optional

# %%
#|hide
show_doc(this_module.run_fzf)


# %%
#|export
def run_fzf(terms: List[str], disp_terms: Optional[List[str]]=None):
    """
    Launches the fzf command-line fuzzy finder with a list of terms and returns
    the selected term.

    Parameters:
    terms (List[str]): A list of strings to be presented to fzf for selection.

    Returns:
    str or None: The selected string from fzf, or None if no selection was made
    or if fzf encountered an error.

    Raises:
    RuntimeError: If fzf is not installed or not found in the system PATH.
    """
    import subprocess
    if disp_terms is None: disp_terms = terms
    try:
        # Launch fzf with the list of strings
        result = subprocess.run(
            ['fzf'],
            input='\n'.join(disp_terms),
            text=True,
            capture_output=True
        )
        res_term = result.stdout.strip()
        term_index = [t.strip() for t in disp_terms].index(res_term)
        sel_term = terms[term_index]
        # Return the selected string or None if no selection was made
        if result.returncode != 0: 
            return None, None
        else: 
            return term_index, sel_term
    except FileNotFoundError:
        raise RuntimeError("fzf is not installed or not found in PATH.")
