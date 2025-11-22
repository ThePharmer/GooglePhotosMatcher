---
id: 003
priority: p1
status: completed
category: performance
created: 2025-11-22
effort: small
agents: performance-oracle
---

# Fix O(n²) Performance Bug from list.index() in Main Loop

## Problem Statement

In `main.py:31`, `list.index(entry)` performs O(n) linear search on every iteration of the O(n) loop, creating O(n²) overall complexity.

```python
progress = round(obj.index(entry)/len(obj)*100, 2)
```

For 10,000 files, this results in ~50 million operations instead of 10,000.

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py` (line 31)

## Proposed Solution

Use `enumerate()` for O(1) index access:

```python
for idx, entry in enumerate(obj):
    if entry.is_file() and entry.name.endswith(".json"):
        progress = round(idx / len(obj) * 100, 2)
```

## Impact

- 10,000 file processing: ~50x slower than necessary
- Processing time scales quadratically with file count
- Poor user experience with large Google Takeout exports

## Acceptance Criteria

- [ ] Replace `obj.index(entry)` with `enumerate()` pattern
- [ ] Progress calculation remains accurate
- [ ] Performance improvement verified with large file sets
