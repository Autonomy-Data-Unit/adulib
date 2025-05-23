# %% [markdown]
# # daemons

# %%
#|default_exp utils.daemons

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.utils.daemons as this_module

# %%
#|export
import time
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
import os


# %%
#|export
def create_watchdog_daemon(
    folder_path: str,
    lock_file: str,
    callback: Callable[[object], None],
    recursive: bool = True,
    verbose: bool = False,
) -> Callable[[], None]:
    """
    Starts a background daemon that watches `folder_path` for changes.
    Calls `callback(event)` whenever a file changes.

    Args:
        folder_path: The path to watch for changes.
        callback: The function to call when a file changes. Receives the event as argument.
        recursive: Whether to watch the folder recursively.
        lock_file: Optional path to a lock file to ensure only one daemon is running.

    Returns:
        A function to start the daemon thread, or a no-op function if locked.
    """
    if lock_file and os.path.exists(lock_file):
        if verbose: print(f"[watchdog_daemon] Lock file exists at {lock_file}. Daemon will not start.")
        return None, None

    # Write PID or timestamp for traceability
    with open(lock_file, "w") as f:
        f.write(f"{os.getpid()} - {time.ctime()}\n")

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            callback(event)

    observer = Observer()
    event_handler = _Handler()
    observer.schedule(event_handler, path=folder_path, recursive=recursive)

    def _start():
        observer.start()
        if verbose: print(f"[watchdog_daemon] Watching: {folder_path}")
        try:
            while True:
                time.sleep(1)
                if not os.path.exists(lock_file): break
        except KeyboardInterrupt:
            observer.stop()
        if verbose: print("[watchdog_daemon] Daemon stopped.")
        observer.join()
        if lock_file and os.path.exists(lock_file):
            os.remove(lock_file)

    thread = Thread(target=_start, daemon=True)

    def start():
        thread.start()

    def stop():
        observer.stop()
        observer.join()
        if lock_file and os.path.exists(lock_file):
            os.remove(lock_file)

    return start, stop


# %%
import tempfile
from pathlib import Path

def my_callback(event):
    print("Folder changed!", event)

lock_file_path = tempfile.mktemp()
daemon_start, daemon_stop = create_watchdog_daemon(Path("/tmp/random_folder").expanduser(), lock_file_path, my_callback, verbose=True)
daemon_start()
time.sleep(0.1)
_daemon_start, _daemon_stop = create_watchdog_daemon(Path("/tmp/random_folder").expanduser(), lock_file_path, my_callback, verbose=True)
assert _daemon_start is None
daemon_stop()
_daemon_start, _daemon_stop = create_watchdog_daemon(Path("/tmp/random_folder").expanduser(), lock_file_path, my_callback, verbose=True)
assert _daemon_start is not None
