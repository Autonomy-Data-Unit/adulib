# %% [markdown]
# # config
#
# Utilities for setting up and managing configurations in a project.

# %%
#|default_exp config

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.config as this_module

# %%
#|export
from pathlib import Path
from typing import Any
from pydantic import BaseModel, model_validator, ConfigDict


# %%
#|export
class PathRef(BaseModel):
    model_config = ConfigDict(extra='forbid')
    parent: str|None = None
    path: Path
    
    @model_validator(mode='before')
    @classmethod
    def process_path(cls, data: Any) -> Any:
        if isinstance(data, str): data = {'path': data}
        data['path'] = Path(data['path'])
        if not data.get('parent') and not Path(data['path']).expanduser().is_absolute(): 
            raise ValueError(f"The '{data}' must be an absolute path if 'parent' is noe specified.")
        return data


# %%
#|export
class PkgConfig(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    @classmethod
    def _post_process(cls, obj: 'PkgConfig') -> Any:
        def get_path(key) -> Path:
            val = getattr(obj, key)
            if isinstance(val, PathRef) and val.parent is None:
                val = val.path
            if isinstance(val, PathRef):
                return get_path(val.parent) / val.path
            else:
                return Path(val).expanduser().resolve()
        
        for key in cls.model_fields:
            value = getattr(obj, key)
            # Dereference PathRef instances and turn into Path objects
            if isinstance(value, PathRef):
                setattr(obj, key, get_path(key))
            # If the value is a string or Path, but the field type is PathRef, convert it to an expanded Path
            elif isinstance(value, (str, Path)) and issubclass(cls.model_fields[key].annotation, PathRef):
                setattr(obj, key, Path(value).expanduser().resolve())
        return obj
    
    @classmethod
    def from_toml(cls, toml_path: str) -> 'PkgConfig':
        import toml
        toml_config = toml.load(toml_path)
        return cls.model_validate(toml_config)
    
    def impart(self, target_obj):
        """
        Imparts the configuration values to the target object.
        The target object should have attributes matching the config keys.
        """
        for key, value in self.model_dump().items():
            setattr(target_obj, key, value)


# %%
class FooConfig(PkgConfig):
    my_path1: PathRef
    my_path2: PathRef
    my_path3: PathRef = '/an/absolute/path/'
    my_path4: PathRef = '~/my/path4'
    my_path5: PathRef = Path('~/my/path5')
    my_path6: PathRef|None = None
    my_path7: PathRef|None
    
foo = FooConfig(
    my_path1 = "~/my/path1",
    my_path2 = PathRef(parent='my_path1', path='subdir/my_path2'),
    my_path7 = "~/my/path7",
)

assert isinstance(foo.my_path1, Path) and foo.my_path1 == Path('~/my/path1').expanduser().resolve()
assert isinstance(foo.my_path2, Path) and foo.my_path2 == foo.my_path1 / 'subdir/my_path2'
assert isinstance(foo.my_path3, Path) and foo.my_path3 == Path('/an/absolute/path/')
assert isinstance(foo.my_path4, Path) and foo.my_path4 == Path('~/my/path4').expanduser().resolve()
assert isinstance(foo.my_path5, Path) and foo.my_path5 == Path('~/my/path5').expanduser().resolve()
assert foo.my_path6 is None
assert isinstance(foo.my_path7, Path) and foo.my_path7 == Path('~/my/path7').expanduser().resolve()
