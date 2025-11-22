---
id: 016
priority: p1
status: pending
category: testing
created: 2025-11-22
effort: medium
agents: kieran-python-reviewer
---

# Add Unit Tests with pytest

## Problem Statement

The codebase has no automated tests, making it risky to refactor or add new features without accidentally breaking existing functionality.

## Affected Files

- `/home/user/GooglePhotosMatcher/files/auxFunctions.py`
- `/home/user/GooglePhotosMatcher/files/main.py`

## Proposed Solution

Create a `tests/` directory with pytest test files:

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_fix_title.py     # Test fixTitle() sanitization
├── test_search_media.py  # Test searchMedia() patterns
├── test_check_same_name.py # Test duplicate naming
└── test_exif.py          # Test EXIF operations
```

### Key Test Cases

1. **fixTitle()**
   - Path traversal attempts (`../../../etc/passwd`)
   - Dangerous characters removal
   - Unicode handling

2. **searchMedia()**
   - Edited file detection
   - Truncated filename handling (47 char limit)
   - Duplicate (1), (2) naming

3. **checkIfSameName()**
   - Returns original when not in set
   - Increments correctly
   - Raises ValueError at max_attempts

4. **set_EXIF()**
   - DateTime fields set correctly
   - GPS coordinates conversion

## Impact

- No safety net for refactoring
- Bugs discovered in production
- Cannot implement CI/CD

## Acceptance Criteria

- [ ] pytest configured in pyproject.toml or setup.cfg
- [ ] >80% code coverage on auxFunctions.py
- [ ] All critical paths have test cases
- [ ] Tests run in <10 seconds
- [ ] CI-ready (can run headless)
