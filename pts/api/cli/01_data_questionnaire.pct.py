# %% [markdown]
# # 01_data_questionnaire

# %%
#|default_exp cli.data_questionnaire

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.cli.data_questionnaire as this_module

# %%
#|export
from typing import Any, Dict, List, Union, Optional, Type, get_args, get_origin
import inspect
import enum

# %%
#|exporti
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin
from pydantic import BaseModel
import questionary
import inspect
import enum


def is_optional(field_type: Any) -> bool:
    origin = get_origin(field_type)
    args = get_args(field_type)
    return origin is Union and type(None) in args

def get_inner_type(field_type: Any) -> Any:
    if get_origin(field_type) is Union:
        return next(arg for arg in get_args(field_type) if arg is not type(None))
    return field_type


def prompt_for_value(field_name: str, field_type: Any, default: Optional[Any] = None) -> Any:
    field_type = get_inner_type(field_type)

    # Enum
    if inspect.isclass(field_type) and issubclass(field_type, enum.Enum):
        choices = [e.name for e in field_type]
        default_name = default.name if isinstance(default, field_type) else None
        selected = questionary.select(f"{field_name} (choose one)", choices=choices, default=default_name).ask()
        return field_type[selected]

    # Bool
    if field_type is bool:
        return questionary.confirm(f"{field_name}?", default=bool(default)).ask()

    # Int, Float, Str
    if field_type is int:
        return int(questionary.text(f"{field_name} (int):", default=str(default) if default is not None else "").ask())
    if field_type is float:
        return float(questionary.text(f"{field_name} (float):", default=str(default) if default is not None else "").ask())
    if field_type is str:
        return questionary.text(f"{field_name}:", default=str(default) if default else "").ask()

    # Nested model
    if inspect.isclass(field_type) and issubclass(field_type, BaseModel):
        print(f"\n-- {field_name} (nested model) --")
        return data_questionnaire(field_type, default or {})

    raise NotImplementedError(f"prompt_for_value does not support type: {field_type}")


def prompt_for_list(field_name: str, item_type: Any, initial: Optional[list] = None) -> list:
    values = initial[:] if initial else []
    while True:
        add_more = questionary.confirm(f"Add item to {field_name}?", default=not values).ask()
        if not add_more:
            break
        values.append(prompt_for_value(f"{field_name} item", item_type))
    return values


def prompt_for_dict(field_name: str, value_type: Any, initial: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = initial.copy() if initial else {}
    while True:
        add_more = questionary.confirm(f"Add key-value pair to {field_name}?", default=not data).ask()
        if not add_more:
            break
        key = questionary.text(f"Enter key for {field_name}:").ask()
        value = prompt_for_value(f"Value for {key} in {field_name}", value_type)
        data[key] = value
    return data




# %%
#|export
def data_questionnaire(
    model_cls: Type[BaseModel],
    initial_data: Optional[Dict[str, Any]] = None,
    print_final: bool = True,
) -> BaseModel:
    initial_data = initial_data or {}
    responses = {}

    questionary.print(f"Filling in model for {model_cls.__name__}")

    for name, field in model_cls.model_fields.items():
        raw_type = field.annotation
        field_type = get_inner_type(raw_type)
        default = initial_data.get(name, field.default if not field.is_required() else None)

        # Prompt to skip optional or defaulted fields
        if is_optional(raw_type) or not field.is_required():
            fill = questionary.confirm(f"Do you want to fill in '{name}'?", default=default is not None).ask()
            if not fill:
                continue

        origin = get_origin(field_type)

        if origin == list:
            item_type = get_args(field_type)[0]
            responses[name] = prompt_for_list(name, item_type, default)
        elif origin == dict:
            key_type, value_type = get_args(field_type)
            if key_type != str:
                raise NotImplementedError("Only dicts with string keys are supported.")
            responses[name] = prompt_for_dict(name, value_type, default)
        else:
            responses[name] = prompt_for_value(name, field_type, default)

    data = model_cls(**responses)

    if print_final:
        from rich import print as rprint
        questionary.print("Responses:")
        rprint(data.model_dump())

    return data

# %% [markdown]
# Example:
#
# ```python
# from typing import List, Dict
# from pydantic import BaseModel
# import enum
#
# class Role(enum.Enum):
#     ADMIN = "admin"
#     USER = "user"
#     GUEST = "guest"
#
# class Tag(BaseModel):
#     label: str
#     score: int
#
# class Preferences(BaseModel):
#     dark_mode: bool
#     language: str
#
# class UserProfile(BaseModel):
#     username: str
#     age: int
#     primary_role: Role
#     roles: List[Role]
#     preferences: Preferences
#     skills: List[str]
#     tags: List[Tag]
#     notes: Dict[str, str]
#     projects: Dict[str, Tag]
#     
#     
# user = data_questionnaire(UserProfile, initial_data={
#     'username': 'lukas',
#     'primary_role' : Role.USER,
#     'preferences': {
#         'language': 'en'
#     },
#     'roles': [Role.USER, Role.ADMIN],
#     'tags': [
#         Tag(label='tag1', score=1),
#     ]
# })
# ```
