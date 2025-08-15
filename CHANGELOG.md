## [0.4.0] - 2025-08-15

### 🚀 Features

- *(adulib.llm)* Call logs are now also cached, and are retrieved by llm functions. For all llm functions but 'token_counter', a boolean 'cache_hit' and the 'call_log' is returned by default.

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- New publish scripts
- Update version in pyproject.toml
## [0.3.11] - 2025-08-14

### 🚀 Features

- *(adulib.config)* Utilities for managing project configuration

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.3.10] - 2025-08-13

### 🚀 Features

- *(utils.wrangle)* More helpful error message when max cols reached in 'flatten_records_to_df'
- *(algos.smart_dedup)* Added arguemnts 'use_fuzzy_str_matching' and 'use_embedding_matching'
- *(utils)* Utils.set_func_defaults

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.9] - 2025-07-12

### 🚀 Features

- *(utils.wrangle)* Added many features to the flatten functions

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.8] - 2025-07-12

### 🚀 Features

- *(utils.wrangle)* Updated the default separator for nested fields to '.' in 'flatten_records_to_df'
- *(utils.wrangle)* Added 'keep_unflattened' argument to 'flatten_records_to_df' and 'flatten_dict'

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.7] - 2025-07-12

### 🚀 Features

- *(utils.wrangle)* 'flatten_dict' and 'flatten_records_to_df'

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.6] - 2025-07-10

### 🚀 Features

- *(utils.pipes)* Added support for '>>' as well

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.5] - 2025-07-10

### 🚀 Features

- *(adulib.utils.pipes)* Added 'papply_mask'

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.4] - 2025-07-10

### 🚀 Features

- *(utils.wrangle)* Utilities for data wrangling. Added pipes for them as well.

### 📚 Documentation

- Added another example

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.3] - 2025-07-05

### 🚀 Features

- *(smart_dedup)* Sort output to ensure consistent output
- *(adulib.algos.smart_dedup)* Added argument 'entity_embeddings'
- *(adulib.algos.smart_dedup)* Added check that 'entity_embeddings' are of correct length.

### 🐛 Bug Fixes

- *(adulib.algos.smart_dedup)* System_prompt and prompt_template were not being used.

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update docs
- Update version in pyproject.toml
## [0.3.2] - 2025-07-05

### 🚀 Features

- *(adulib.utils.pipes)* Added pto_pkl and pfrom_pkl
- *(adulib.utils.pipes)* Pipes for dataframe and json files

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.1] - 2025-07-05

### 🚀 Features

- *(adulib.utils.pipes)* New submodule adulib.utils.pipes. Various utility functions to do piping in Python.

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update version in pyproject.toml
## [0.3.0] - 2025-07-03

### 🚀 Features

- *(llm.embeddings)* 'batch_embeddings' and 'async_batch_embeddings'
- *(algos)* Adulib.llm.str_matching. Util functions to do string matching. Currently supports fuzzy string matching and matching using embeddings.
- *(algos)* Smart_dedup

### 🐛 Bug Fixes

- *(utils)* Bug in run_script

### 📚 Documentation

- *(reflection)* Added documentation
- *(asynchronous)* Cleaned up output cell
- *(git)* Cleaned up output cell
- *(llm.completions)* Cleaned up output cell
- *(utils.daemon)* Cleaned up output cell
- Removed errors in the docs and signature for 'single' and 'async_single'
- *(llm.embeddings)* Improved function signature docs
- *(llm.completions)* Improved function signature docs
- *(llm.text_completions)* Improved function signature docs

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Ran 'nbl prepare -f'
- Updated uv.lock
- Updated publish script
- Update docs
- Update version in pyproject.toml
## [0.2.1] - 2025-06-20

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update docs
- Update docs
- Update version in pyproject.toml
## [0.2.0] - 2025-05-26

### 🚀 Features

- *(adulib.llm.completions)* Renamed `prompt` to `single`. Renamed the `context` argument to `system`. Added multi-turn feature for `single`.

### 🐛 Bug Fixes

- Cache_args were not passed properly

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.13] - 2025-05-26

### 🚀 Features

- Prompt and async_prompt now has a default context

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.12] - 2025-05-26

### 🐛 Bug Fixes

- Completions were crashing even if cache_path was set, if the default one had not been set

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.11] - 2025-05-26

### 🚀 Features

- Cli.data_questionnaire

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.10] - 2025-05-24

### 🚀 Features

- Added interval daemon
- Cli.run_fzf
- Git.find_root_repo_path

### 🐛 Bug Fixes

- Returns a 'stop' method for when the watchdog is already running
- Updated __init__.py with new modules

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.9] - 2025-05-23

### 🐛 Bug Fixes

- Create_watchdog_daemon now creates folders if they dont exist

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.8] - 2025-05-23

### 🚀 Features

- Can now specify multiple folders in create_watchdog_daemon

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.7] - 2025-05-23

### 🚀 Features

- Utils.daemon

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.6] - 2025-05-23

### 🚀 Features

- Adulib.reflection.mod_property

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.5] - 2025-05-22

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.4] - 2025-05-21

### 🐛 Bug Fixes

- Bug in call logging
- Call logging bug

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Nbl prepare
- Update version in pyproject.toml
## [0.1.3] - 2025-05-20

### 🐛 Bug Fixes

- Call logging

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Update version in pyproject.toml
## [0.1.2] - 2025-05-20

### 📚 Documentation

- Added example to adulib.llm.prompt
- Minor change

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Ran 'nbl prepare'
- Rendered docs
- Ran 'nbl prepare'
- Update version in pyproject.toml
## [0.1.1] - 2025-05-07

### 🚀 Features

- Updated completions documentation to include some info on 'prompt' up top
- Updated readme

### 🐛 Bug Fixes

- Necessary dependencies were in 'dev' rather than in the main dependency group

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG.md
- Nbl readme
- Updated dependencies in lock
- Update version in pyproject.toml
## [0.1.0] - 2025-05-05

### 🚀 Features

- Improved caching. Now will allow for a global default cache, but must deliberately set it.
- Adulib.llm is now a wrapper around litellm
- *(llm)* Retrying on exceptions
- Timeouts for llm calls

### 🐛 Bug Fixes

- Added attributes for doc generation

### 💼 Other

- Update CHANGELOG.md

### ⚙️ Miscellaneous Tasks

- Litellm dependency
- Re-rendered docs and cleaned
- Update version in pyproject.toml
## [0.0.5] - 2025-04-30

### 🚀 Features

- Async memoize

### ⚙️ Miscellaneous Tasks

- Updated CHANGELOG
- Updated publish script
- V0.0.5
## [0.0.4] - 2025-04-30

### 🚀 Features

- Utils.run_script

### 🐛 Bug Fixes

- Removed old nbdev export cells

### 🚜 Refactor

- Had to rejig some stuff to get the package versioning work
- Moved over to nblite
- Cleaned up adulib.llm

### ⚙️ Miscellaneous Tasks

- Updated readme with better uv sync command
- Uv.lock
- V0.0.4
## [0.0.3] - 2025-03-25

### ⚙️ Miscellaneous Tasks

- Nbdev_export
## [0.0.2] - 2025-03-06

### 🐛 Bug Fixes

- Put the changelog update after the tag is updated.
- Adulib.llm and adulib.rest will not raise ImportError if the correct packages have not been installed.
- Changed the eviction policy to none and the max size to (practically) infinite in adulib.llm and adulib.rest

### 🚜 Refactor

- Changed ImportError message
- Changed name from src to api
## [0.0.1] - 2025-02-16

### 🚀 Features

- Updated  publish_new_version.sh

### 🐛 Bug Fixes

- Set put_version_in_init=False in settings.ini

### ⚙️ Miscellaneous Tasks

- Set up system for publishing versions
- Added 'publish_new_version.sh'
