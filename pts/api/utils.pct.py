# %% [markdown]
# # utils
#
# General utility functions.

# %%
#|default_exp utils

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
import subprocess, os
from pathlib import Path
import tempfile

# %%
import adulib.utils as this_module

# %%
#|hide
show_doc(this_module.as_dict)


# %%
#|export
def as_dict(**kwargs):
    """
    Convert keyword arguments to a dictionary.
    """
    return kwargs


# %%
#|hide
show_doc(this_module.check_mutual_exclusivity)


# %%
#|export
def check_mutual_exclusivity(*args, check_falsy=True):
    """
    Check if only one of the arguments is falsy (or truthy, if check_falsy is False).
    """
    if check_falsy:
        return sum(bool(x) for x in args) == 1
    else:
        return sum(bool(x) for x in args) == 1


# %%
#|hide
show_doc(this_module.run_script)


# %%
#|export
def run_script(script_path: Path, cwd: Path = None, env: dict = None, interactive: bool = False, raise_on_error: bool = True):
    """Execute a Python or Bash script with specified parameters and environment variables.

    Args:
        script_path (Path): Path to the script file to execute (.py or .sh)
        cwd (Path, optional): Working directory for script execution. Defaults to None.
        env (dict, optional): Additional environment variables to pass to the script. Defaults to None.
        interactive (bool, optional): Whether to run the script in interactive mode. Defaults to False.
        raise_on_error (bool, optional): Whether to raise an exception on non-zero exit code. Defaults to True.

    Returns:
        tuple: A tuple containing:
            - int: Return code from the script execution
            - str or None: Standard output (None if interactive mode)
            - bytes: Contents of the temporary output file

    Raises:
        FileNotFoundError: If the specified script does not exist
        ValueError: If the script type is not supported (.py or .sh)
        Exception: If the script fails and raise_on_error is True

    Notes:
        - The script's output can be captured in two ways:
          1. Through stdout/stderr capture when not in interactive mode
          2. Through a temporary file accessible via the OUT_PATH environment variable
        - In interactive mode, the script uses the parent process's stdin/stdout/stderr
    """
    if not script_path.exists():
        raise FileNotFoundError(f"Script '{script_path}' not found in {const.scripts_path}.")
    
    if script_path.suffix == '.sh':
        interpreter = "bash"
    elif script_path.suffix == '.py':
        interpreter = "python"
    else:
        raise ValueError(f"Unsupported script type: {script_path.suffix}.")
    
    cmd = [interpreter, script_path]
    
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        cmd_env = {
            **os.environ,
            **(env or {}),
            "OUT_PATH": temp_file.name
        }
        
        if not interactive:
            result = subprocess.run(
                cmd,
                cwd=Path(cwd).as_posix() if cwd is not None else None,
                env=cmd_env,
                capture_output=True,
                text=True
            )
            ret_code = result.returncode
            ret_stdout = result.stdout
        else:
            process = subprocess.Popen(
                cmd,
                stdin=None,  # Use the parent's stdin
                stdout=None, # Use the parent's stdout
                stderr=None, # Use the parent's stderr
                cwd=cwd,
                env=cmd_env
            )
            ret_code = process.wait()
            ret_stdout = None # No stdout since it is interactive
            
        output = temp_file.read()
        
    if raise_on_error and ret_code != 0:
        raise Exception(f"Script '{script_path}' failed with return code {ret_code}")
        
    return ret_code, ret_stdout, output
