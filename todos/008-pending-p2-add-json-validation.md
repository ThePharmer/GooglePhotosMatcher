---
id: 008
priority: p2
status: pending
category: security
created: 2025-11-22
effort: medium
agents: security-sentinel
---

# Add JSON Schema Validation

## Problem Statement

JSON data is accessed using direct dictionary key access without validating the structure. Malformed JSON files could cause unhandled exceptions.

```python
titleOriginal = data['title']                          # main.py:37
timeStamp = int(data['photoTakenTime']['timestamp'])  # main.py:54
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py` (lines 37, 54, 72)

## Proposed Solution

```python
def validate_json_structure(data: dict) -> bool:
    """Validate required JSON fields exist and have correct types."""
    required_fields = ['title', 'photoTakenTime']
    for field in required_fields:
        if field not in data:
            return False

    if 'timestamp' not in data.get('photoTakenTime', {}):
        return False

    # Validate timestamp is reasonable
    try:
        timestamp = int(data['photoTakenTime']['timestamp'])
        if timestamp < 0 or timestamp > 4102444800:  # Up to year 2100
            return False
    except (ValueError, TypeError):
        return False

    return True
```

## Impact

- KeyError exceptions crashing application
- Poor user experience with corrupted JSON files
- Silent data loss

## Acceptance Criteria

- [ ] JSON structure validated before access
- [ ] Missing fields handled gracefully with error message
- [ ] Invalid timestamps rejected
- [ ] User notified of problematic files
