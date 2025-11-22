---
id: 012
priority: p2
status: pending
category: documentation
created: 2025-11-22
effort: small
agents: architecture-strategist
---

# Add requirements.txt for Dependency Management

## Problem Statement

No dependency specification file exists. Users cannot easily install dependencies or set up the development environment.

## Affected Files

- Project root (missing file)

## Proposed Solution

Create `requirements.txt`:

```
Pillow>=9.0.0
PySimpleGUI>=4.60.0
piexif>=1.1.3
win32-setctime>=1.1.0; sys_platform == 'win32'
```

Or create `pyproject.toml` for modern Python packaging:

```toml
[project]
name = "google-photos-matcher"
version = "1.2.0"
dependencies = [
    "Pillow>=9.0.0",
    "PySimpleGUI>=4.60.0",
    "piexif>=1.1.3",
    "win32-setctime>=1.1.0; sys_platform == 'win32'",
]
```

## Impact

- Cannot reproducibly install the project
- No version pinning causes "works on my machine" issues
- Cannot set up CI/CD pipelines

## Acceptance Criteria

- [ ] requirements.txt or pyproject.toml created
- [ ] All dependencies listed with version constraints
- [ ] Platform-specific dependencies marked appropriately
- [ ] README updated with installation instructions
