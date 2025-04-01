# %% [markdown]
# # adulib.reflection
#
# Utilities for Python reflection.

# %%
#|default_exp reflection

# %%
#|hide
import nblite; from nbdev.showdoc import show_doc; nblite.nbl_export()

# %%
#|export
from pathlib import Path
import os
import sys
import importlib
import inspect
import types
import functools
import keyword
import re

# %%
import adulib.reflection

# %%
show_doc(adulib.reflection.is_valid_python_name)


# %%
#|export
def is_valid_python_name(name: str) -> bool:
    for name_part in name.split('.'):
        if keyword.iskeyword(name_part):
            return False
        valid_identifier_pattern = r'^[A-Za-z_][A-Za-z0-9_]*$'
        if not re.match(valid_identifier_pattern, name_part): return False
    return True


# %%
show_doc(adulib.reflection.find_module_root)


# %%
#|export
def find_module_root(path):
    path = Path(path)
    path = path if path.is_dir() else path.parent
    is_module = '__init__.py' in [p.parts[-1] for p in path.glob('*')]
    if not is_module: return None
    else:
        parent_module = find_module_root(path.parent)
        if parent_module is None: return path
        else: return parent_module


# %%
show_doc(adulib.reflection.get_module_path_hierarchy)


# %%
#|exporti
def __get_module_path_hierarchy(path, hierarchy):
    path = Path(path)
    if not path.exists(): raise FileNotFoundError(f"No file or directory found at: {path}")
    if path.is_file():
        if path.suffix != '.py': raise ValueError(f"File '{path}' is not a python file.")
        is_in_module = '__init__.py' in [p.parts[-1] for p in path.parent.glob('*')]
        if is_in_module:
            module_name = path.stem
            hierarchy.append((module_name, path))
            __get_module_path_hierarchy(path.parent, hierarchy)
    else:
        is_module = '__init__.py' in [p.parts[-1] for p in path.glob('*')]
        if is_module:
            module_name = path.stem
            hierarchy.append((module_name, path))
            __get_module_path_hierarchy(path.parent, hierarchy)


# %%
#|export        
def get_module_path_hierarchy(path):
    hierarchy = []
    __get_module_path_hierarchy(path, hierarchy)
    return hierarchy


# %%
show_doc(adulib.reflection.get_function_from_py_file)


# %%
#|export
def get_function_from_py_file(file_path, func_name=None, args=[], is_async=False, return_func_key=''):
    file_path = Path(file_path)
    module_path = find_module_root(file_path)
    is_in_module = module_path is not None
    
    # Check if the file exists
    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    if not file_path.exists():
        raise FileNotFoundError(f"No file found at: {file_path}")
    
    if func_name is None:
        func_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Read the contents of the file
    with open(file_path, 'r') as file:
        func_body_code = file.read()
        
    if not func_body_code.strip(): func_body_code = 'pass'
    
    # Tabify
    func_body_code = '\n'.join(list(map(lambda line: f"    {line}", func_body_code.split('\n'))))
    if return_func_key:
        args = [return_func_key] + args
    func_code = f"{'async ' if is_async else ''}def {func_name}({', '.join(args)}):\n{func_body_code}"
    
    if is_in_module:
        # This all is necessary to allow for relative imports in the code
        sys.path.insert(0, module_path.parent.absolute().as_posix())
        module_hierarchy = get_module_path_hierarchy(file_path)
        module_hierarchy_str = '.'.join([e[0] for e in reversed(module_hierarchy)])
        module_spec = importlib.util.spec_from_file_location(module_hierarchy_str, file_path.absolute().as_posix())
        code_module = importlib.util.module_from_spec(module_spec)
        locals_dict = code_module.__dict__
    else:
        locals_dict = {}
        
    exec(func_code, locals_dict)
    if is_in_module: sys.path.pop(0)
    
    func = locals_dict[func_name]
    # Create a new code object with the correct filename and line number. This will allow for proper displaying of the line number and code during exceptions.
    new_code = types.CodeType(
        func.__code__.co_argcount,
        func.__code__.co_posonlyargcount,
        func.__code__.co_kwonlyargcount,
        func.__code__.co_nlocals,
        func.__code__.co_stacksize,
        func.__code__.co_flags,
        func.__code__.co_code,
        func.__code__.co_consts,
        func.__code__.co_names,
        func.__code__.co_varnames,
        file_path.as_posix(),
        func.__code__.co_name,
        func.__code__.co_qualname,
        func.__code__.co_firstlineno, # Line number offset. Not entirely sure why it's -1, but it works.
        func.__code__.co_lnotab,
        func.__code__.co_exceptiontable,
        func.__code__.co_freevars,
        func.__code__.co_cellvars
    )
    func.__code__ = new_code
    
    if return_func_key:
        if is_async:
            async def _func(*args):
                return_val = []
                def return_func(val): return_val.append(val)
                await func(return_func, *args)
                return return_val[0]
        else:
            def _func(*args):
                return_val = []
                def return_func(val): return_val.append(val)
                func(return_func, *args)
                return return_val[0]
        return _func
    else:
        return func


# %%
import tempfile

# %%
py_code = """
print('Hello...')
print(f'...{name}!')
"""

with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
    temp_file.write(py_code.encode('utf-8'))
    temp_file_path = temp_file.name

func = get_function_from_py_file(temp_file_path, args=['name'])
func('world')

# %%
py_code = """
import asyncio
await asyncio.sleep(0)
print('Hello...')
print(f'...{name}!')
"""

with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
    temp_file.write(py_code.encode('utf-8'))
    temp_file_path = temp_file.name

func = get_function_from_py_file(temp_file_path, is_async=True, args=['name'])
await func('world')

# %%
show_doc(adulib.reflection.method_from_py_file)


# %%
#|export
def method_from_py_file(file_path:str):
    def decorator(orig_func):
        args = list(inspect.signature(orig_func).parameters.keys())
        is_async = inspect.iscoroutinefunction(orig_func)
        new_func = get_function_from_py_file(file_path, func_name=orig_func.__name__, args=args, is_async=is_async)
        if is_async:
            @functools.wraps(orig_func)
            async def wrapped_method(*args, **kwargs):
                await new_func(*args, **kwargs)
                await orig_func(*args, **kwargs)
        else:
            @functools.wraps(orig_func)
            def wrapped_method(*args, **kwargs):
                new_func(*args, **kwargs)
                orig_func(*args, **kwargs)
        return wrapped_method
    return decorator


# %%
py_code = """
print(f'Hello {self.name}')
"""

with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
    temp_file.write(py_code.encode('utf-8'))
    temp_file_path = temp_file.name

class TestClass:
    def __init__(self, name):
        self.name = name

    @method_from_py_file(temp_file_path)
    def print_name(self): pass
    
TestClass("world").print_name()
