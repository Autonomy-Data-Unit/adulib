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
from typing import List, Union, Tuple, Any

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
#|exporti
def __helper_flatten_dict(
    d,
    prefix,
    preserve,
    keep,
    discard,
) -> dict:
    items = []
    for k, v in d.items():
        new_key = tuple(list(prefix) + [k]) if prefix else (k,)
        if discard is not None and new_key in discard: continue
        if keep is not None and not any(new_key == _k[:len(new_key)] or _k == new_key[:len(_k)] for _k in keep): continue
        if isinstance(v, dict) and new_key not in preserve:
            items.extend(__helper_flatten_dict(v, new_key, preserve=preserve, keep=keep, discard=discard))
        elif isinstance(v, list) and new_key not in preserve:
            for i, item in enumerate(v):
                indexed_key = tuple(list(new_key) + [i])
                if isinstance(item, dict) and indexed_key not in preserve:
                    items.extend(__helper_flatten_dict(item, indexed_key, preserve=preserve, keep=keep, discard=discard))
                else:
                    items.append((indexed_key, item))
        else:
            items.append((new_key, v))
    return items


# %%
#|export
def flatten_dict(
    d,
    sep='.',
    preserve: List[Any] = None,
    keep: List[Union[str, Tuple[str]]] = None,
    discard: List[Union[str, Tuple[str]]] = None,
) -> dict:
    """
    Flatten a nested dictionary into a single-level dictionary with compound keys.

    This function recursively flattens dictionaries and lists. Nested keys are concatenated 
    using a separator (default is '.'). Lists are flattened by appending the index 
    to the key. Nested dictionaries and lists within lists are also handled.

    Nested keys for `preserve`, `keep`, and `discard` can be specified either as strings
    in the form "{key}{sep}{child_key}..." or as tuples of keys.

    Args:
        d (dict): The dictionary to flatten.
        sep (str, optional): Separator to use between concatenated keys. Defaults to '.'.
        preserve (List[Any], optional): List of compound keys to preserve as nested structures.
            If a key matches, its value will not be flattened further.
        keep (List[Union[str, Tuple[str]]], optional): If provided, only these top-level keys will be kept.
            Cannot be used with 'discard'.
        discard (List[Union[str, Tuple[str]]], optional): If provided, these top-level keys will be excluded.
            Cannot be used with 'keep'.

    Returns:
        dict: A new flattened dictionary with compound keys.

    Raises:
        ValueError: If both 'keep' and 'discard' are specified.

    Examples:
        >>> data = {
        ...     'key1': 'val',
        ...     'key2': [1, 2, 3],
        ...     'key3': {
        ...         'foo': 'bar',
        ...         'baz': [1, 2, 3],
        ...         'qux': {
        ...             'key4': 'value',
        ...             'key5': [4, 5, 6]
        ...         }
        ...     }
        ... }
        >>> flatten_dict(data)
        {'key1': 'val', 'key2.0': 1, 'key2.1': 2, 'key2.2': 3, 'key3.foo': 'bar', 'key3.baz.0': 1, 'key3.baz.1': 2, 'key3.baz.2': 3, 'key3.qux.key4': 'value', 'key3.qux.key5.0': 4, 'key3.qux.key5.1': 5, 'key3.qux.key5.2': 6}

        >>> flatten_dict(data, preserve=['key3.qux'])
        {'key1': 'val', 'key2.0': 1, 'key2.1': 2, 'key2.2': 3, 'key3.foo': 'bar', 'key3.baz.0': 1, 'key3.baz.1': 2, 'key3.baz.2': 3, 'key3.qux': {'key4': 'value', 'key5': [4, 5, 6]}}

        >>> flatten_dict(data, preserve=[('key3', 'qux')]) # Equivalent to the previous example
        {'key1': 'val', 'key2.0': 1, 'key2.1': 2, 'key2.2': 3, 'key3.foo': 'bar', 'key3.baz.0': 1, 'key3.baz.1': 2, 'key3.baz.2': 3, 'key3.qux': {'key4': 'value', 'key5': [4, 5, 6]}}


        >>> flatten_dict(data, keep=['key2'])
        {'key2.0': 1, 'key2.1': 2, 'key2.2': 3}

        >>> flatten_dict(data, discard=['key3'])
        {'key1': 'val', 'key2.0': 1, 'key2.1': 2, 'key2.2': 3}
    """
    if keep is not None and discard is not None:
        raise ValueError("Cannot specify both 'keep' and 'discard'.")
    if keep is not None: keep = [tuple(k.split(sep)) if type(k) != tuple else k for k in keep]
    if discard is not None: discard = [tuple(k.split(sep)) if type(k) != tuple else k for k in discard]
    preserve = preserve or []
    preserve = [tuple(k.split(sep)) if type(k) != tuple else k for k in preserve]
    items = __helper_flatten_dict(d, '', preserve, keep, discard)
    items = [(sep.join(map(str, k)), v) for k, v in items]
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
flatten_dict(data, preserve=[('key3', 'qux')])

# %%
flatten_dict(data, preserve=['key3.qux'])

# %%
flatten_dict(data, keep=['key2'])

# %%
flatten_dict(data, keep=['key3.qux'])

# %%
flatten_dict(data, keep=[('key3', 'qux')])

# %%
flatten_dict(data, discard=['key3'])

# %%
#|hide
show_doc(this_module.flatten_records_to_df)


# %%
#|export
def flatten_records_to_df(
    records : List[dict],
    col_prefix='',
    sep='.',
    max_cols=None,
    preserve: List[Any] = None,
    keep: List[Union[str, Tuple[str]]] = None,
    discard: List[Union[str, Tuple[str]]] = None,
):
    """
    Flattens a list of (potentially nested) dictionaries into a pandas DataFrame.

    Each dictionary in the input list is flattened using compound keys for nested structures.
    Lists within dictionaries are expanded with indexed keys. The resulting DataFrame has one row per record.

    Nested keys for `preserve`, `keep`, and `discard` can be specified either as strings
    in the form "{key}{sep}{child_key}..." or as tuples of keys.

    Args:
        records (List[dict]): List of dictionaries to flatten.
        col_prefix (str, optional): Prefix to add to all column names. Defaults to ''.
        sep (str, optional): Separator to use between concatenated keys. Defaults to '.'.
        max_cols (int, optional): Maximum allowed number of columns. Raises ValueError if exceeded.
        preserve (List[Any], optional): List of compound keys to preserve as nested structures.
        keep (List[Union[str, Tuple[str]]], optional): Only these top-level keys will be kept. Cannot be used with 'discard'.
        discard (List[Union[str, Tuple[str]]], optional): These top-level keys will be excluded. Cannot be used with 'keep'.

    Returns:
        pd.DataFrame: DataFrame with flattened records as rows.

    Raises:
        ValueError: If both 'keep' and 'discard' are specified, or if max_cols is exceeded.

    Examples:
        >>> records = [
        ...     {'name': 'Alice', 'age': 30, 'address': {'city': 'Wonderland', 'zip': '12345'}},
        ...     {'name': 'Bob', 'age': 25, 'address': {'city': 'Builderland', 'zip': '67890'}}
        ... ]
        >>> flatten_records_to_df(records)
           name  age      address.city address.zip
        0 Alice   30      Wonderland      12345
        1   Bob   25     Builderland      67890

        >>> flatten_records_to_df(records, preserve=['address'])
           name  age                        address
        0 Alice   30   {'city': 'Wonderland', 'zip': '12345'}
        1   Bob   25  {'city': 'Builderland', 'zip': '67890'}
    """
    cols = []
    flattened_records = []
    for record in records:
        flattened = flatten_dict(record, sep=sep, preserve=preserve, keep=keep, discard=discard)
        if col_prefix:
            flattened = {f"{col_prefix}{k}": v for k, v in flattened.items()}
        flattened_records.append(flattened)
        cols.extend([k for k in flattened.keys() if k not in cols])
        if max_cols is not None and len(cols) > max_cols:
            raise ValueError(f"Maximum number of columns ({max_cols}) exceeded.\nCols: {cols}.")
    return pd.DataFrame(flattened_records)


# %%
records = [
    {'name': 'Alice', 'age': 30, 'address': {'city': 'Wonderland', 'zip': '12345'}},
    {'name': 'Bob', 'age': 25, 'address': {'city': 'Builderland', 'zip': '67890'}},
    {'name': 'Charlie', 'age': 35, 'address': {'city': 'Chocolate Factory', 'zip': '54321'}}
]

flatten_records_to_df(records)

# %%
flatten_records_to_df(records, preserve=['address'])

# %%
flatten_records_to_df(records, discard=['address'])

# %%
try:
    flatten_records_to_df(records, max_cols=2)
except ValueError as e:
    print(e)
