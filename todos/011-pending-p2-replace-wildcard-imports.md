---
id: 011
priority: p2
status: pending
category: code-quality
created: 2025-11-22
effort: small
agents: architecture-strategist, kieran-python-reviewer
---

# Replace Wildcard Imports with Explicit Imports

## Problem Statement

Both files use `from module import *` which violates PEP 8, pollutes namespaces, and hides dependencies.

```python
from auxFunctions import *  # main.py:1
from main import *          # window.py:1
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py` (line 1)
- `/home/user/GooglePhotosMatcher/files/window.py` (line 1)

## Proposed Solution

```python
# main.py
from auxFunctions import (
    searchMedia,
    fixTitle,
    checkIfSameName,
    createFolders,
    setWindowsTime,
    set_EXIF,
)

# window.py
from main import mainProcess
```

## Impact

- Namespace pollution and symbol collision risk
- Static analysis tools fail
- IDE autocompletion broken
- Hidden dependencies

## Acceptance Criteria

- [ ] All imports are explicit
- [ ] `__all__` defined in auxFunctions.py
- [ ] No `import *` statements remain
- [ ] IDE autocompletion works correctly
