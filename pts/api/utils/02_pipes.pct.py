# %% [markdown]
# # 02_pipes

# %%
#|default_exp utils.pipes

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.utils.pipes as this_module

# %%
#|export
import pipe
import tempfile
import pickle

# %% [markdown]
# ## Mathematical operations

# %%
#|export
psum = pipe.Pipe(lambda x, start=0: sum(x, start=start))
pmin = pipe.Pipe(lambda x, key=(lambda y:y): min(x, key=key))
pmax = pipe.Pipe(lambda x, key=(lambda y:y): max(x, key=key))
pabs = pipe.Pipe(lambda x: abs(x))
padd = pipe.Pipe(lambda x, y: x + y)
psub = pipe.Pipe(lambda x, y: x - y)
pmul = pipe.Pipe(lambda x, y: x * y)
pdiv = pipe.Pipe(lambda x, y: x / y)
pmod = pipe.Pipe(lambda x, y: x % y)

# %%
[2,3,4] | psum(start=1) == sum([2,3,4], start=1)

# %%
[(5,2), (3,1), (4,2), (6,3)] | pmin(key=lambda x: x[0]) 

# %%
2 | padd(3) | psub(2) | pmul(4) | pdiv(2) | pmod(10)

# %% [markdown]
# ## Type conversions

# %%
#|export
ptype = pipe.Pipe(lambda x, typ: typ(x))
plist = pipe.Pipe(lambda x: list(x))
ptuple = pipe.Pipe(lambda x: tuple(x))
pdict = pipe.Pipe(lambda x: dict(x))
pset = pipe.Pipe(lambda x: set(x))
pint = pipe.Pipe(lambda x: int(x))
pfloat = pipe.Pipe(lambda x: float(x))
pstr = pipe.Pipe(lambda x: str(x))
pbool = pipe.Pipe(lambda x: bool(x))

# %%
[1,6,2,6,2,4,6,7] | pset

# %% [markdown]
# ## String operations

# %%
#|export
pjoin = pipe.Pipe(lambda x, sep: sep.join(str(i) for i in x))
psplit = pipe.Pipe(lambda x, sep=None, maxsplit=-1: x.split(sep, maxsplit=maxsplit))
pstrip = pipe.Pipe(lambda x, chars=None: x.strip(chars))
plstrip = pipe.Pipe(lambda x, chars=None: x.lstrip(chars))
prstrip = pipe.Pipe(lambda x, chars=None: x.rstrip(chars))
pupper = pipe.Pipe(lambda x: x.upper())
plower = pipe.Pipe(lambda x: x.lower())

# %%
"hello world!" | pupper | prstrip("!") | psplit | pjoin("    ")

# %% [markdown]
# ## Function operations

# %%
#|export
pbind = pipe.Pipe(lambda x, f, *args, **kwargs: lambda *args2, **kwargs2: f(x, *args, *args2, **kwargs, **kwargs2))
ppartial = pipe.Pipe(lambda f, *args, **kwargs: lambda *args2, **kwargs2: f(*args, *args2, **kwargs, **kwargs2))
papply = pipe.Pipe(lambda x, f: f(x))
pcall = pipe.Pipe(lambda f, *args, **kwargs: f(*args, **kwargs))


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

pflatten = pipe.Pipe(lambda x, levels=None: _pflatten_helper(x, 0, levels))
plen = pipe.Pipe(lambda x: len(x))

# %%
#|export
pmap = pipe.map
puniq = pipe.uniq
ptranspose = pipe.transpose
pfilter = pipe.filter
psort = pipe.sort
pt = pipe.t
penumerate = pipe.enumerate
pzip = pipe.izip
pslice = pipe.islice

pbatched = pipe.batched
pchain = pipe.chain
pchain_with = pipe.chain_with
pdedup = pipe.dedup
pgroupby = pipe.groupby
ppermutations = pipe.permutations
preverse = pipe.reverse
pskip_while = pipe.skip_while
ptail = pipe.tail
ptake = pipe.take
ptake_while = pipe.take_while
ptraverse = pipe.traverse

# %%
[1, [2, [3, [4, 5]]]] | pflatten | plist

# %%
[1, 2, 3, [4, 5, 6, [7, 8, 9]]] | pflatten(levels=1) | plist

# %% [markdown]
# ## Misc operations

# %%
#|export
pget = pipe.Pipe(lambda x, k: x[k])
pgetattr = pipe.Pipe(lambda x, k: getattr(x, k))
ptee = pipe.tee

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
@pipe.Pipe
def pwrite(content, file_path=None, mode='w'):
    if file_path is None:
        file_path = tempfile.NamedTemporaryFile(delete=False).name
    with open(file_path, mode) as f:
        f.write(content)
    return file_path
    
@pipe.Pipe
def pread(file_path, mode='r'):
    with open(file_path, mode) as f:
        return f.read()
    
@pipe.Pipe
def pto_pkl(obj, file_path=None):
    """Write an object to a pickle file."""
    if file_path is None:
        file_path = tempfile.NamedTemporaryFile(delete=False).name
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)
    return file_path
    
@pipe.Pipe
def pfrom_pkl(file_path):
    """Read a pickle file and return the object."""
    with open(file_path, 'rb') as f:
        return pickle.load(f)
    
pshow = pipe.Pipe(lambda x: print(x) or x)  # Returns x for chaining

# %%
"hello world" | pwrite | pread

# %%
"hello world" | pshow

# %%
{'key': 'value'} | pto_pkl | pfrom_pkl
