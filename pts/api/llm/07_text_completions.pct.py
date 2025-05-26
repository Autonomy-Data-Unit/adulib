# %% [markdown]
# # text_completions
#
# > See the [`litellm` documention](https://docs.litellm.ai/docs/text_completion).

# %%
#|default_exp llm.text_completions

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
try:
    import litellm
    import functools
    from adulib.llm._utils import _llm_func_factory, _llm_async_func_factory
    from adulib.llm.tokens import token_counter
except ImportError as e:
    raise ImportError(f"Install adulib[llm] to use this API.") from e

# %%
#|hide
from adulib.caching import set_default_cache_path
import adulib.llm.text_completions as this_module

# %%
#|hide
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')

# %% [markdown]
# Text completions generate a continuation of a single prompt string, making them ideal for tasks like autocomplete, code completion, or single-turn text generation. This is contrast to chat completions, which are meant for multi-turn conversations, where the input is a list of messages with roles (like "user" and "assistant"), allowing the model to maintain context and produce more coherent, context-aware responses across multiple exchanges. Use text completions for simple, stateless tasks, and chat completions for interactive, context-dependent scenarios.

# %%
#|echo: false
show_doc(this_module.text_completion)

# %%
#|export
text_completion = _llm_func_factory(
    func=litellm.text_completion,
    func_name="text_completion",
    func_cache_name="text_completion",
    retrieve_log_data=lambda model, func_kwargs, response, cache_args: {
        "method": "text_completion",
        "input_tokens": token_counter(model=model, text=func_kwargs['prompt'], **cache_args),
        "output_tokens": sum([token_counter(model=model, text=c.text, **cache_args) for c in response.choices]),
        "cost": response._hidden_params['response_cost'],
    }
)

text_completion.__doc__ = """
This function is a wrapper around a corresponding function in the `litellm` library, see [this](https://docs.litellm.ai/docs/text_completion) for a full list of the available arguments.
""".strip()

# %%
response = text_completion(
    model="gpt-4o-mini",
    prompt="1 + 1 = ",
)
response.choices[0].text

# %%
#|echo: false
show_doc(this_module.async_text_completion)

# %%
#|export
async_text_completion = _llm_async_func_factory(
    func=functools.wraps(litellm.text_completion)(litellm.atext_completion), # This is needed as 'litellm.atext_completion' lacks the right signature
    func_name="async_text_completion",
    func_cache_name="text_completion",
    retrieve_log_data=lambda model, func_kwargs, response, cache_args: {
        "method": "text_completion",
        "input_tokens": token_counter(model=model, text=func_kwargs['prompt'], **cache_args),
        "output_tokens": sum([token_counter(model=model, text=c.text, **cache_args) for c in response.choices]),
        "cost": response._hidden_params['response_cost'],
    }
)

text_completion.__doc__ = """
This function is a wrapper around a corresponding function in the `litellm` library, see [this](https://docs.litellm.ai/docs/text_completion) for a full list of the available arguments.
""".strip()

# %%
response = await async_text_completion(
    model="gpt-4o-mini",
    prompt="1 + 2 = ",
)
response.choices[0].text
