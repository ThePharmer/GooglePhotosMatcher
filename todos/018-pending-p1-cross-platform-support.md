---
id: 018
priority: p1
status: completed
category: compatibility
created: 2025-11-22
effort: medium
agents: architecture-strategist, kieran-python-reviewer
---

# Add Linux and macOS Support

## Problem Statement

The application only works on Windows due to the `win32_setctime` dependency. Linux and macOS users cannot use the tool.

## Affected Files

- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (setWindowsTime function)
- `/home/user/GooglePhotosMatcher/requirements.txt`

## Proposed Solution

1. Create platform-aware time setting function:

```python
import platform
import os
from datetime import datetime

def set_file_times(filepath: str, timestamp: int) -> None:
    """Set file creation and modification times cross-platform."""

    # Set modification time (works on all platforms)
    date = datetime.fromtimestamp(timestamp)
    mod_time = time.mktime(date.timetuple())
    os.utime(filepath, (mod_time, mod_time))

    # Set creation time (platform-specific)
    system = platform.system()

    if system == "Windows":
        from win32_setctime import setctime
        setctime(filepath, timestamp)
    elif system == "Darwin":  # macOS
        import subprocess
        date_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y %H:%M:%S")
        subprocess.run(["SetFile", "-d", date_str, filepath], check=False)
    else:  # Linux - creation time not typically supported
        pass  # Modification time already set above
```

2. Update requirements.txt:

```
win32-setctime>=1.1.0; sys_platform == 'win32'
```

3. Add optional macOS dependency note in README

## Impact

- Cannot run on macOS or Linux
- Limits potential user base
- Cannot use in Docker containers

## Acceptance Criteria

- [ ] Works on Windows (existing functionality preserved)
- [ ] Works on macOS (using SetFile or alternative)
- [ ] Works on Linux (graceful degradation for creation time)
- [ ] No crashes on unsupported platforms
- [ ] Platform detected at runtime, not import time
