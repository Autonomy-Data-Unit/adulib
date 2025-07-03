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
from pathlib import Path
from typing import Callable, Union, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread, Lock, Timer
from pathlib import Path
import datetime
import os


# %%
#|export
def create_interval_daemon(
    lock_file: str,
    callback: Callable[[], None],
    interval: float = 1.0,  # seconds between callbacks
    verbose: bool = False,
    error_callback: Callable[[BaseException], None] = None,
) -> Callable[[], None]:
    """
    Creates a daemon that calls the callback function at fixed intervals.

    Args:
        callback: The function to call at each interval.
        interval: Number of seconds between callbacks.
        verbose: Whether to print status messages.

    Returns:
        A (start, stop) function pair for the daemon.
    """
    
    lock_path = Path(lock_file)
    
    def stop():
        if lock_path.exists(): lock_path.unlink()
    
    def wait_for_stop():
        while True:
            if not lock_path.exists(): break
            pid, _ = lock_path.read_text().split(" - ")
            if pid != str(os.getpid()): break
            time.sleep(1)
    
    if lock_path.exists():
        if verbose: print(f"[interval_daemon] Lock file exists at {lock_file}. Daemon will not start.")
        return None, stop, wait_for_stop

    # Write PID and timestamp for traceability
    def write_lock_file():
        with lock_path.open("w") as f:
            f.write(f"{os.getpid()} - {datetime.datetime.now().strftime('%a %b %d %H:%M:%S.%f %Y')}\n")
    write_lock_file()
    
    def _run():
        if verbose: print(f"[interval_daemon] Daemon started with {interval}s interval")
        
        try:
            while True:
                callback()
                time.sleep(interval)
                if not lock_path.exists(): break
                else:
                    pid, _ = lock_path.read_text().split(" - ")
                    if pid != str(os.getpid()): break
                write_lock_file()
        except BaseException as e:
            if error_callback is not None: error_callback(e)
            print(f"[interval_daemon] Error: {e}")
        finally:
            if verbose: print("[interval_daemon] Daemon stopped")
            if lock_path.exists() and lock_path.read_text().split(" - ")[0] == str(os.getpid()): lock_path.unlink()

    def start():
        thread = Thread(target=_run, daemon=True)
        thread.start()

    return start, stop, wait_for_stop


# %%
import tempfile
from pathlib import Path

def my_callback():
    print("Interval callback!")

start, stop, wait_for_stop = create_interval_daemon(tempfile.mktemp(), my_callback, interval=2.0, verbose=True)
start()  # Will print "Interval callback!" every 2 seconds
stop()   # Stops the daemon


# %%
#|export
def create_watchdog_daemon(
    folder_paths: Union[str, List[str]],
    lock_file: str,
    callback: Callable[[object], None],
    recursive: bool = True,
    verbose: bool = False,
    rate_limit: float = 1, # per second
) -> Callable[[], None]:
    """
    Starts a background daemon that watches `folder_paths` for changes.
    Calls `callback(event)` whenever a file changes.

    Args:
        folder_paths: A path or list of paths to watch.
        callback: The function to call when a file changes. Receives the event as argument.
        recursive: Whether to watch folders recursively.
        lock_file: Optional path to a lock file to ensure only one daemon is running.
        rate_limit: Minimum number of seconds between callbacks.

    Returns:
        A (start, stop) function pair for the daemon.
    """
    if not isinstance(folder_paths, list):
        folder_paths = [folder_paths]
    
    if lock_file and os.path.exists(lock_file):
        if verbose: print(f"[watchdog_daemon] Lock file exists at {lock_file}. Daemon will not start.")
        def stop():
            if lock_file and os.path.exists(lock_file): 
                os.remove(lock_file)
        return None, stop

    # Write PID and timestamp for traceability
    with open(lock_file, "w") as f:
        f.write(f"{os.getpid()} - {time.ctime()}\n")

    # Fixed-rate debouncing setup
    last_callback_time = 0
    pending_event = None
    timer_lock = Lock()

    def debounced_callback(event):
        nonlocal last_callback_time, pending_event
        
        with timer_lock:
            current_time = time.time()
            time_since_last_callback = current_time - last_callback_time
            
            # Store the most recent event
            pending_event = event
            
            # If enough time has passed since last callback, execute immediately
            if time_since_last_callback >= rate_limit:
                callback(pending_event)
                last_callback_time = current_time
                pending_event = None
            else:
                # Schedule the callback for the remaining time
                wait_time = rate_limit - time_since_last_callback
                
                def execute_callback():
                    with timer_lock:
                        nonlocal last_callback_time, pending_event
                        if pending_event is not None:  # Only execute if we still have a pending event
                            callback(pending_event)
                            last_callback_time = time.time()
                            pending_event = None
                
                Timer(wait_time, execute_callback).start()

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            debounced_callback(event)

    observer = Observer()
    event_handler = _Handler()
    for path in folder_paths:
        if not os.path.isdir(path):
            if not os.path.exists(path):
                Path(path).mkdir(parents=True, exist_ok=True)
        observer.schedule(event_handler, path=path, recursive=recursive)

    def _start():
        observer.start()
        if verbose: print(f"[watchdog_daemon] Daemon started.")
        try:
            while True:
                time.sleep(1)
                if not os.path.exists(lock_file): break
        except BaseException as e:
            if verbose: print(f"[watchdog_daemon] Error: {e}")
        finally:
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
        if lock_file and os.path.exists(lock_file): os.remove(lock_file)

    return start, stop


# %%
import tempfile
from pathlib import Path

def my_callback(event):
    print("Folder changed!", event)

lock_file_path = tempfile.mktemp()
daemon_start, daemon_stop = create_watchdog_daemon("/bin", lock_file_path, my_callback, verbose=False, recursive=False)
daemon_start()
time.sleep(0.1)
_daemon_start, _daemon_stop = create_watchdog_daemon("/bin", lock_file_path, my_callback, verbose=False, recursive=False)
assert _daemon_start is None
daemon_stop()
_daemon_start, _daemon_stop = create_watchdog_daemon(["/bin", "/"], lock_file_path, my_callback, verbose=False, recursive=False)
assert _daemon_start is not None
_daemon_start()
time.sleep(0.1)
_daemon_stop()
