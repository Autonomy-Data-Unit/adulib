# %% [markdown]
# # 03_wrangle

# %%
#|default_exp utils.wrangle

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.utils.wrangle as this_module

# %%
#|export
import pandas as pd

# %%
#|hide
show_doc(this_module.df_to_tsv)


# %%
#|export
def df_to_tsv(df: pd.DataFrame, include_index: bool = False) -> str:
    """
    Converts a DataFrame to a tab-separated string.
    Useful for copying to Excel or Google Sheets.
    """
    return df.to_csv(sep='\t', index=include_index)


# %%
df = pd.DataFrame([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
])
df_to_tsv(df)

# %%
#|hide
show_doc(this_module.df_to_clipboard)


# %%
#|export
def df_to_clipboard(df: pd.DataFrame, include_index: bool = False):
    """
    Converts a DataFrame to a tab-separated string and copies it to the clipboard,
    so it can be pasted directly into Google Sheets or Excel.
    
    Args:
        df (pd.DataFrame): The DataFrame to copy.
        include_index (bool): Whether to include the index in the output.
    """
    import pyperclip
    pyperclip.copy(df_to_tsv(df, include_index))
