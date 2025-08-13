# LockFileSemaphore

A production-grade **file-based semaphore** to control concurrent access to shared resources across multiple processes or machines.

Includes atomic lock creation, stale lock recovery, timeout handling, and context manager support.

## Installation

```bash
pip install LockFileSemaphore
```

## Example Usage

### Traditional style:

```python
from LockFileSemaphore import begin_semaphore_ops, end_semaphore_ops

lock_id = begin_semaphore_ops("/tmp/resource.lock") #put path to lock file here , may be arbitrary
try:
    # Critical section
    pass
finally:
    end_semaphore_ops("/tmp/resource.lock", lock_id)
```

### Context Manager style:

```python
from LockFileSemaphore import FileLock

with FileLock("/tmp/resource.lock"): #put path to lock file here, may be arbitrary
    # Critical section
    pass
```

## Features

- Atomic file lock creation (O_CREAT | O_EXCL)
- Stale lock detection and automatic cleanup
- Timeout and retry interval configuration
- Context manager support
- Cross-platform compatibility
