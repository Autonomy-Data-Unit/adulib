# adulib

> Tools and utilities for the Autonomy Data Unit (ADU)


The lifecycle of a shared ADU utility or tool is as follows:

1. Implement the utility in this repo.
2. If the utility grows in complexity, it should be moved to its own dedicated package, and will be included in `adulib` as a (potentially optional) dependency.

<!-- #region -->
# Development install instructions

## Prerequisites

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Install [direnv](https://direnv.net/) to automatically load the project virtual environment when entering it.
    - Mac: `brew install direnv`
    - Linux: `curl -sfL https://direnv.net/install.sh | bash`

## Setting up the environment

Run the following:

```bash
# CD into the root of the repo folder
uv sync --all-extras # Installs the virtual environment at './.venv'
direnv allow # Allows the automatic running of the script './.envrc'
nbl install-hooks # Installs some git hooks that ensures that notebooks are added properly
```

You are now set up to develop the codebase.

Further instructions:

- To export notebooks run `nbl export`.
- To clean notebooks run `nbl clean`.
- To see other available commands run just `nbl`.
- To add a new dependency run `uv add package-name`. See the the [uv documentation](https://docs.astral.sh/uv/) for more details.
- You need to git add all 'twinned' notebooks for the commit to be validated. For example, if you add `nbs/my-nb.ipynb`, you must also add `pts/my-nb.pct.py`.
- To render the documentation, run `nbl render-docs`. To preview it run `nbl preview-docs`
<!-- #endregion -->
