# %% [markdown]
# # base

# %%
#|default_exp llm.base

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
try:
    import litellm
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
from adulib.caching import set_default_cache_path
import adulib.llm.base as this_module

# %%
#|hide
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')

# %%
#|export
available_models = list(litellm.model_cost.keys())
available_models.remove("sample_spec")


# %%
#|export
def search_models(query: str):
    return [model for model in available_models if query.lower() in model.lower()]


# %%
search_models('gpt-4o')
