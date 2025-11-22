---
id: 021
priority: p2
status: pending
category: feature
created: 2025-11-22
effort: small
agents: architecture-strategist
---

# Add Configuration File Support

## Problem Statement

Users must re-enter settings (edited suffix, output folder names) every time they run the application. There's no way to save preferences.

## Affected Files

- New file: `/home/user/GooglePhotosMatcher/files/config.py`
- `/home/user/GooglePhotosMatcher/files/main.py`
- `/home/user/GooglePhotosMatcher/files/window.py`

## Proposed Solution

1. Create config module:

```python
# files/config.py
from __future__ import annotations
import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

CONFIG_FILE = Path.home() / ".google-photos-matcher.json"

@dataclass
class Config:
    edited_suffix: str = "editado"
    output_folder: str = "MatchedMedia"
    raw_folder: str = "EditedRaw"
    last_path: Optional[str] = None
    log_level: str = "INFO"
    log_file: Optional[str] = None

    @classmethod
    def load(cls) -> Config:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                return cls(**data)
        return cls()

    def save(self) -> None:
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)
```

2. Integrate with GUI:

```python
# window.py
config = Config.load()

# Pre-fill input with saved value
[sg.InputText(default_text=config.edited_suffix, key='-INPUT_TEXT-')]

# Save on successful run
config.last_path = values["-IN2-"]
config.edited_suffix = values['-INPUT_TEXT-']
config.save()
```

3. CLI support:

```bash
# Use config file
google-photos-matcher /path/to/takeout

# Override config
google-photos-matcher /path/to/takeout --edited-suffix "edited"

# Save to config
google-photos-matcher --set edited_suffix=edited
```

## Impact

- Repetitive data entry
- Cannot standardize across multiple runs
- No persistence of preferences

## Acceptance Criteria

- [ ] Config file created at `~/.google-photos-matcher.json`
- [ ] GUI loads and saves preferences
- [ ] CLI respects config, allows overrides
- [ ] Invalid config handled gracefully (reset to defaults)
- [ ] Config location can be overridden with env var
