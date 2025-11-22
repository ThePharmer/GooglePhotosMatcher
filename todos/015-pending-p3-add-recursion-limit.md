---
id: 015
priority: p3
status: completed
category: security
created: 2025-11-22
effort: small
agents: security-sentinel, performance-oracle
---

# Add Recursion Limit to checkIfSameName()

## Problem Statement

The `checkIfSameName()` function uses unbounded recursion. With many duplicate filenames, it could cause stack overflow.

```python
def checkIfSameName(title, titleFixed, mediaMoved, recursionTime):
    if titleFixed in mediaMoved:
        return checkIfSameName(...)  # No limit!
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (lines 61-66)

## Proposed Solution

Convert to iterative or add limit:

```python
def checkIfSameName(title: str, media_moved: set[str], max_attempts: int = 1000) -> str:
    base, ext = os.path.splitext(title)
    if title not in media_moved:
        return title

    for i in range(1, max_attempts + 1):
        candidate = f"{base}({i}){ext}"
        if candidate not in media_moved:
            return candidate

    raise ValueError(f"Could not find unique name for {title} after {max_attempts} attempts")
```

## Impact

- Denial of Service through stack overflow
- Memory exhaustion with many duplicates

## Acceptance Criteria

- [ ] Recursion converted to iteration or limited
- [ ] Clear error message when limit exceeded
- [ ] Works correctly with set-based mediaMoved
