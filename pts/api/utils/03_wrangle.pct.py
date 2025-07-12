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
from typing import List

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


# %%
#|hide
show_doc(this_module.flatten_dict)


# %%
#|export
def flatten_dict(d, prefix='', sep='.', keep_unflattened: List[str] = None):
    """
    Flatten a nested dictionary into a single-level dictionary with compound keys.

    This function recursively flattens dictionaries and lists. Nested keys are concatenated 
    using a separator (default is an underscore). Lists are flattened by appending the index 
    to the key. Nested dictionaries and lists within lists are also handled.

    Args:
        d (dict): The dictionary to flatten.
        prefix (str, optional): The base key to use for the current level of recursion. 
                                    Used internally during recursion. Defaults to ''.
        sep (str, optional): Separator to use between concatenated keys. Defaults to '.'.

    Returns:
        dict: A new flattened dictionary with compound keys.
    """
    items = []
    keep_unflattened = keep_unflattened or []
    for k, v in d.items():
        new_key = f"{prefix}{sep}{k}" if prefix else k
        if isinstance(v, dict) and new_key not in keep_unflattened:
            items.extend(flatten_dict(v, new_key, sep=sep, keep_unflattened=keep_unflattened).items())
        elif isinstance(v, list) and new_key not in keep_unflattened:
            for i, item in enumerate(v):
                indexed_key = f"{new_key}{sep}{i}"
                if isinstance(item, dict) and indexed_key not in keep_unflattened:
                    items.extend(flatten_dict(item, indexed_key, sep=sep, keep_unflattened=keep_unflattened).items())
                else:
                    items.append((indexed_key, item))
        else:
            items.append((new_key, v))
    return dict(items)


# %%
data = {
	'key1' : 'val',
	'key2' : [1, 2, 3],
	'key3' : {
		'foo' : 'bar',
		'baz' : [1, 2, 3],
        'qux' : {
            'key4' : 'value',
            'key5' : [4, 5, 6]
        }
	}
}

flatten_dict(data)

# %%
flatten_dict(data, keep_unflattened=['key3.qux'])

# %%
#|hide
show_doc(this_module.flatten_records_to_df)


# %%
#|export
def flatten_records_to_df(records, col_prefix='', sep='.', max_cols=None, keep_unflattened: List[str] = None):
    """
    Flattens a list of (potentially nested) dictionaries into a pandas DataFrame.

    Each dictionary in the input list is flattened using compound keys for nested structures.
    Lists within dictionaries are expanded with indexed keys. The resulting DataFrame has one row per record.

    Args:
        records (list): List of dictionaries to flatten.
        col_prefix (str, optional): Prefix to add to all column names. Defaults to ''.
        sep (str, optional): Separator to use between concatenated keys. Defaults to '.'.
        max_cols (int, optional): Maximum allowed number of columns. Raises ValueError if exceeded.

    Returns:
        pd.DataFrame: DataFrame with flattened records as rows.
    """
    cols = set()
    flattened_records = []
    for record in records:
        flattened = flatten_dict(record, prefix=col_prefix, sep=sep, keep_unflattened=keep_unflattened)
        flattened_records.append(flattened)
        cols.update(flattened.keys())
        if max_cols is not None and len(cols) >= max_cols:
            raise ValueError(f"Maximum number of columns ({max_cols}) exceeded.")
    return pd.DataFrame(flattened_records)


# %%
records = [
    {'name': 'Alice', 'age': 30, 'address': {'city': 'Wonderland', 'zip': '12345'}},
    {'name': 'Bob', 'age': 25, 'address': {'city': 'Builderland', 'zip': '67890'}},
    {'name': 'Charlie', 'age': 35, 'address': {'city': 'Chocolate Factory', 'zip': '54321'}}
]

flatten_records_to_df(records)

# %%
flatten_records_to_df(records, keep_unflattened=['address'])
