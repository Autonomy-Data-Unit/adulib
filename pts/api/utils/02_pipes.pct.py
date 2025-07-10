# %% [markdown]
# # 02_pipes

# %%
#|default_exp utils.pipes

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
import pipe


# %%
#|exporti
class Pipe:
    def __init__(self, func):
        self.__doc__ = func.__doc__
        self.func = func

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self.func(x, *args, **kwargs))

    def __rrshift__(self, other):
        return self.func(other)
    
    def __ror__(self, other):
        return self.func(other)
    
class ConvertedPipe:
    """Class to convert a `pipe.Pipe` to also be compatible with the `>>` operator."""
    def __init__(self, old_pipe):
        self.old_pipe = old_pipe

    def __call__(self, *args, **kwargs):
        return self.old_pipe(*args, **kwargs)

    def __rrshift__(self, other):
        return self.old_pipe.__ror__(other)
    
    def __ror__(self, other):
        return self.old_pipe.__ror__(other)


# %% [markdown]
# ## Mathematical operations

# %%
#|export
psum = Pipe(lambda x, start=0: sum(x, start=start))
pmin = Pipe(lambda x, key=(lambda y:y): min(x, key=key))
pmax = Pipe(lambda x, key=(lambda y:y): max(x, key=key))
pabs = Pipe(lambda x: abs(x))
padd = Pipe(lambda x, y: x + y)
psub = Pipe(lambda x, y: x - y)
pmul = Pipe(lambda x, y: x * y)
pdiv = Pipe(lambda x, y: x / y)
pmod = Pipe(lambda x, y: x % y)

# %%
[2,3,4] | psum(start=1) == sum([2,3,4], start=1)

# %%
[(5,2), (3,1), (4,2), (6,3)] | pmin(key=lambda x: x[0]) 

# %%
2 | padd(3) | psub(2) | pmul(4) | pdiv(2) | pmod(10)

# %%
(
    2 
        | padd(3)
        | psub(2)
        | pmul(4)
        | pdiv(2)
        | pmod(10)
)

# %% [markdown]
# ## Type conversions

# %%
#|export
ptype = Pipe(lambda x, typ: typ(x))
plist = Pipe(lambda x: list(x))
ptuple = Pipe(lambda x: tuple(x))
pdict = Pipe(lambda x: dict(x))
pset = Pipe(lambda x: set(x))
pint = Pipe(lambda x: int(x))
pfloat = Pipe(lambda x: float(x))
pstr = Pipe(lambda x: str(x))
pbool = Pipe(lambda x: bool(x))

# %%
[1,6,2,6,2,4,6,7] | pset

# %% [markdown]
# ## String operations

# %%
#|export
pjoin = Pipe(lambda x, sep: sep.join(str(i) for i in x))
psplit = Pipe(lambda x, sep=None, maxsplit=-1: x.split(sep, maxsplit=maxsplit))
pstrip = Pipe(lambda x, chars=None: x.strip(chars))
plstrip = Pipe(lambda x, chars=None: x.lstrip(chars))
prstrip = Pipe(lambda x, chars=None: x.rstrip(chars))
pupper = Pipe(lambda x: x.upper())
plower = Pipe(lambda x: x.lower())

# %%
"hello world!" | pupper | prstrip("!") | psplit | pjoin("    ")

# %% [markdown]
# ## Function operations

# %%
#|export
pbind = Pipe(lambda x, f, *args, **kwargs: lambda *args2, **kwargs2: f(x, *args, *args2, **kwargs, **kwargs2))
ppartial = Pipe(lambda f, *args, **kwargs: lambda *args2, **kwargs2: f(*args, *args2, **kwargs, **kwargs2))
papply = Pipe(lambda x, f: f(x))
pcall = Pipe(lambda f, *args, **kwargs: f(*args, **kwargs))


# %%
def square(x):
    return x**2

5 | pbind(square) | pcall

# %%
(lambda: 10) | pcall

# %%
(lambda x, y: x + y) | ppartial(2) | ppartial(3) | pcall


# %% [markdown]
# ## Collection operations

# %%
#|export
def _pflatten_helper(lst, curr_level, levels=None):
    """Helper function to flatten a nested list."""
    if levels is not None and curr_level > levels:
        yield lst
        return
    for item in lst:
        if isinstance(item, list):
            yield from _pflatten_helper(item, curr_level+1, levels)
        else:
            yield item

pflatten = Pipe(lambda x, levels=None: _pflatten_helper(x, 0, levels))
plen = Pipe(lambda x: len(x))

# %%
#|export
pmap = ConvertedPipe(pipe.map)
puniq = ConvertedPipe(pipe.uniq)
ptranspose = ConvertedPipe(pipe.transpose)
pfilter = ConvertedPipe(pipe.filter)
psort = ConvertedPipe(pipe.sort)
pt = ConvertedPipe(pipe.t)
penumerate = ConvertedPipe(pipe.enumerate)
pzip = ConvertedPipe(pipe.izip)
pslice = ConvertedPipe(pipe.islice)

pbatched = ConvertedPipe(pipe.batched)
pchain = ConvertedPipe(pipe.chain)
pchain_with = ConvertedPipe(pipe.chain_with)
pdedup = ConvertedPipe(pipe.dedup)
pgroupby = ConvertedPipe(pipe.groupby)
ppermutations = ConvertedPipe(pipe.permutations)
preverse = ConvertedPipe(pipe.reverse)
pskip_while = ConvertedPipe(pipe.skip_while)
ptail = ConvertedPipe(pipe.tail)
ptake = ConvertedPipe(pipe.take)
ptake_while = ConvertedPipe(pipe.take_while)
ptraverse = ConvertedPipe(pipe.traverse)

# %%
[1, [2, [3, [4, 5]]]] | pflatten | plist

# %%
[1, 2, 3, [4, 5, 6, [7, 8, 9]]] | pflatten(levels=1) | plist

# %%
["Joe", 32, "Mary", 28, "John", 45] | pbatched(2) | pdict

# %% [markdown]
# ## Misc operations

# %%
#|export
pget = Pipe(lambda x, k: x[k])
pgetattr = Pipe(lambda x, k: getattr(x, k))
ptee = ConvertedPipe(pipe.tee)

# %%
{"key1": "value1", "key2": "value2"} | pget("key1")


# %%
class Foo:
    def __init__(self):
        self.x = 123
        
Foo() | pgetattr("x")


# %% [markdown]
# ## File/IO operations

# %%
#|export
@Pipe
def pwrite(content, file_path=None, mode='w'):
    import tempfile
    if file_path is None:
        file_path = tempfile.NamedTemporaryFile(delete=False).name
    with open(file_path, mode) as f:
        f.write(content)
    return file_path
    
@Pipe
def pread(file_path, mode='r'):
    with open(file_path, mode) as f:
        return f.read()
    
pshow = Pipe(lambda x: print(x) or x)  # Returns x for chaining

@Pipe
def pcopy(content):
    """Copy content to clipboard."""
    import pyperclip
    pyperclip.copy(content)
    return content


# %%
"hello world" | pwrite | pread

# %%
"hello world" | pshow


# %% [markdown]
# ## Data wrangling operations

# %%
#|export
@Pipe
def psave_pkl(obj, file_path=None):
    """Write an object to a pickle file."""
    import pickle, tempfile
    if file_path is None:
        file_path = tempfile.NamedTemporaryFile(delete=False).name
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)
    return file_path
    
@Pipe
def pload_pkl(file_path):
    """Read a pickle file and return the object."""
    import pickle
    with open(file_path, 'rb') as f:
        return pickle.load(f)


# %%
{'key': 'value'} | psave_pkl | pload_pkl


# %%
#|export
@Pipe
def pto_df(data, **kwargs):
    """Create a pandas DataFrame."""
    import pandas as pd
    return pd.DataFrame(data, **kwargs)

@Pipe
def pcopy_df(df):
    """
    Copy a DataFrame to clipboard in a format compatible with Google Sheets or Excel.
    
    Usage:
    ```python
    df >> pcopy_df
    ```
    """
    from adulib.utils.wrangle import df_to_clipboard
    df_to_clipboard(df)
    return df

@Pipe
def papply_mask(mask, df):
    """
    Apply a mask to a DataFrame.
    
    Usage:
    ```python
    mask >> papply_mask(df)
    ```
    """
    return df[mask]


# %%
[
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
] | pto_df

# %%
df = {
    'name' : ['Alice', 'Bob'],
    'age' : [30, 25]
} | pto_df
df

# %%
(df['name'] == 'Alice') >> papply_mask(df)


# %%
#|export
@Pipe
def pto_json(data, **kwargs):
    """Convert data to JSON string."""
    import json
    return json.dumps(data, **kwargs)

@Pipe
def pfrom_json(json_str, **kwargs):
    import json
    """Convert JSON string to Python object."""
    return json.loads(json_str, **kwargs)


# %%
{
    'name' : ['Alice', 'Bob'],
    'age' : [30, 25]
} | pto_json | pfrom_json
