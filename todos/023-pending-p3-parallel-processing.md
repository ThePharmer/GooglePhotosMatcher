---
id: 023
priority: p3
status: pending
category: performance
created: 2025-11-22
effort: medium
agents: performance-oracle, kieran-python-reviewer
---

# Add Parallel File Processing

## Problem Statement

Files are processed sequentially, which is slow for large Google Takeout exports (10,000+ files). Modern CPUs have multiple cores that could process files concurrently.

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py`

## Proposed Solution

Use `concurrent.futures` for parallel processing:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProcessResult:
    filename: str
    success: bool
    error: Optional[str] = None

def process_single_file(
    entry: os.DirEntry,
    path: str,
    fixedMediaPath: str,
    nonEditedMediaPath: str,
    editedWord: str,
    piexifCodecs: list[str]
) -> ProcessResult:
    """Process a single JSON file and its associated media."""
    try:
        # ... existing processing logic ...
        return ProcessResult(entry.name, success=True)
    except Exception as e:
        return ProcessResult(entry.name, success=False, error=str(e))

def mainProcess(..., max_workers: int = 4) -> None:
    json_files = [e for e in obj if e.is_file() and e.name.endswith(".json")]

    # Thread pool for I/O-bound operations
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_single_file, entry, path, fixedMediaPath,
                nonEditedMediaPath, editedWord, piexifCodecs
            ): entry
            for entry in json_files
        }

        for future in as_completed(futures):
            result = future.result()
            if result.success:
                successCounter += 1
            else:
                errorCounter += 1
                logger.error(f"{result.filename}: {result.error}")

            # Update progress
            progress = (successCounter + errorCounter) / len(json_files) * 100
            update_progress(window, progress)
```

### Considerations

1. **Thread Safety**
   - `mediaMoved` set needs thread-safe access (use `threading.Lock`)
   - Progress updates need synchronization

2. **Worker Count**
   - Default to `min(4, cpu_count())` for I/O bound work
   - Allow user override via config/CLI

3. **Error Handling**
   - Collect all errors, report at end
   - Don't stop on single file failure

## Performance Estimate

| Files | Sequential | Parallel (4 workers) |
|-------|------------|---------------------|
| 1,000 | ~2 min | ~40 sec |
| 10,000 | ~20 min | ~6 min |
| 50,000 | ~100 min | ~30 min |

## Impact

- Slow processing of large exports
- Poor utilization of modern hardware
- User waiting unnecessarily

## Acceptance Criteria

- [ ] `--workers N` CLI flag
- [ ] Default to sensible auto-detection
- [ ] Thread-safe mediaMoved tracking
- [ ] Progress bar still works correctly
- [ ] No race conditions or data corruption
- [ ] Can be disabled with `--workers 1`
