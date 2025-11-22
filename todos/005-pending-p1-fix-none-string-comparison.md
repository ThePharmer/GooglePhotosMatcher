---
id: 005
priority: p1
status: pending
category: bug
created: 2025-11-22
effort: small
agents: kieran-python-reviewer
---

# Fix None vs "None" String Comparison Bug

## Problem Statement

`searchMedia()` returns `str(realTitle)` which converts `None` to the string `"None"`. The caller then compares against the string literal instead of `None`.

```python
# auxFunctions.py:51
return str(realTitle)  # Converts None to "None"

# main.py:48
if title == "None":  # Comparing to string literal, not None
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (line 51)
- `/home/user/GooglePhotosMatcher/files/main.py` (line 48)

## Proposed Solution

```python
# auxFunctions.py:51
return realTitle  # Don't convert to string

# main.py:48
if title is None:  # Proper None check
```

## Impact

- Type confusion bugs
- Potential false negatives in file matching
- Non-Pythonic code pattern

## Acceptance Criteria

- [ ] `searchMedia()` returns `None` not `"None"`
- [ ] Caller uses `is None` check
- [ ] Type hints added to clarify return type
