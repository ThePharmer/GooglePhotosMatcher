---
id: 020
priority: p2
status: completed
category: feature
created: 2025-11-22
effort: small
agents: code-simplicity-reviewer
---

# Add Dry-Run Preview Mode

## Problem Statement

Users cannot preview what changes will be made before the tool modifies their files. This is risky for:
- Large photo libraries
- Irreplaceable family photos
- First-time users unfamiliar with the tool

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py`
- `/home/user/GooglePhotosMatcher/files/auxFunctions.py`

## Proposed Solution

1. Add dry_run parameter to mainProcess:

```python
def mainProcess(
    browserPath: str,
    window: sg.Window | None,
    editedW: Optional[str],
    dry_run: bool = False
) -> dict[str, Any]:
    """
    Returns:
        Summary dict with planned operations if dry_run=True
    """
    operations = []

    # ... in the processing loop ...
    if dry_run:
        operations.append({
            "action": "move",
            "source": filepath,
            "destination": os.path.join(fixedMediaPath, title),
            "exif_changes": {"DateTime": dateTime, "GPS": (lat, lng)}
        })
    else:
        # Actually perform the operation
        os.replace(filepath, ...)
```

2. Add GUI checkbox or CLI flag:

```python
# GUI
[sg.Checkbox("Preview only (dry run)", key='-DRY_RUN-')]

# CLI
parser.add_argument("-n", "--dry-run", action="store_true")
```

3. Display preview summary:

```
Dry Run Summary:
================
Files to process: 1,234
Files to move: 1,200
Files to skip: 34
EXIF updates: 1,150
Estimated time: ~5 minutes

Proceed? [y/N]
```

## Impact

- Users hesitant to run on important photos
- No way to verify behavior before committing
- Accidents cannot be prevented

## Acceptance Criteria

- [ ] `--dry-run` flag available in CLI
- [ ] Checkbox option in GUI
- [ ] Summary shows: files to move, skip, modify
- [ ] No files modified when dry_run=True
- [ ] Output can be saved to file for review
