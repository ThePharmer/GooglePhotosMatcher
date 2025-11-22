---
id: 001
priority: p1
status: pending
category: bug
created: 2025-11-22
effort: small
agents: security-sentinel, performance-oracle, code-simplicity-reviewer, kieran-python-reviewer
---

# Fix Image Resource Leak - Operating on Closed File Handle

## Problem Statement

In `main.py:59-64`, an image is opened, immediately closed, and then `convert()` is called on the closed handle. This is a critical bug that causes undefined behavior.

```python
im = Image.open(filepath)
im.close()                    # CLOSED HERE
rgb_im = im.convert('RGB')    # BUG: Using closed image!
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py` (lines 59-64)

## Proposed Solution

Use a context manager to properly handle the image lifecycle:

```python
with Image.open(filepath) as im:
    rgb_im = im.convert('RGB')
    new_filepath = filepath.rsplit('.', 1)[0] + ".jpg"
    os.replace(filepath, new_filepath)
    filepath = new_filepath
    rgb_im.save(filepath)
```

## Impact

- Runtime failures during image processing
- Potential memory corruption
- Unpredictable behavior depending on PIL's caching

## Acceptance Criteria

- [ ] Image is properly managed with context manager
- [ ] No operations performed on closed file handles
- [ ] Image conversion works correctly for all supported formats
