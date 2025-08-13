""" 
LockFileSemaphore - Robust File-Based Locking Mechanism (v3)

Provides cross-platform file-based locking for safely serializing access to shared resources.
Includes features like atomic lock acquisition, timeout handling, stale lock recovery, and verbose debugging.
Also supports context manager usage.

Usage Example:

    from LockFileSemaphore import begin_semaphore_ops, end_semaphore_ops, FileLock

    # Traditional usage
    lock_id = begin_semaphore_ops("/tmp/myresource.lock")
    try:
        # Critical section
        pass
    finally:
        end_semaphore_ops("/tmp/myresource.lock", lock_id)

    # Context manager usage
    with FileLock("/tmp/myresource.lock"):
        # Critical section
        pass
"""

import os
import sys
import time
from errno import EACCES, EEXIST
from pathlib import Path

def ensure_directory_exists(path: str | Path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def begin_semaphore_ops(
    path: str | Path,
    timeout: float = 30,
    retry_interval: float = 1,
    max_lock_age: float = 60,
    verbose: bool = False
):
    path = str(path)
    ensure_directory_exists(path)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    mode = 0o644
    start_time = time.time()

    while True:
        try:
            lock_fd = os.open(path, flags, mode)
            if verbose:
                print(f"Lock acquired: {path}")
            return lock_fd
        except OSError as e:
            if e.errno == EEXIST or (e.errno == EACCES and sys.platform == "win32"):
                if max_lock_age is not None:
                    try:
                        lock_age = time.time() - os.path.getmtime(path)
                        if lock_age > max_lock_age:
                            if verbose:
                                print(f"Stale lock detected (age {lock_age:.2f}s), removing lock: {path}")
                            os.remove(path)
                            continue
                    except FileNotFoundError:
                        pass
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Timeout while waiting for lock: {path}")
                time.sleep(retry_interval)
            else:
                raise

def end_semaphore_ops(path: str | Path, LockID: int, verbose: bool = False):
    path = str(path)
    try:
        os.close(LockID)
        os.remove(path)
        if verbose:
            print(f"Lock released: {path}")
    except FileNotFoundError:
        if verbose:
            print(f"Lock file already removed: {path}")
    except Exception as e:
        raise RuntimeError(f"Failed to release lock: {path}") from e

class FileLock:
    """
    Context manager for file-based locking.

    Usage:
        with FileLock("/path/to/lockfile"):
            # critical section
            pass
    """
    def __init__(self, path: str | Path, timeout: float = 30, retry_interval: float = 1, max_lock_age: float = 60, verbose: bool = False):
        self.path = str(path)
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.max_lock_age = max_lock_age
        self.verbose = verbose
        self.lock_id = None

    def __enter__(self):
        self.lock_id = begin_semaphore_ops(
            self.path,
            timeout=self.timeout,
            retry_interval=self.retry_interval,
            max_lock_age=self.max_lock_age,
            verbose=self.verbose
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_id is not None:
            end_semaphore_ops(self.path, self.lock_id, verbose=self.verbose)
