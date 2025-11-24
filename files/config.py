"""Configuration management for Google Photos Matcher."""
from __future__ import annotations

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional

__all__ = ["Config", "CONFIG_FILE", "get_config"]

# Config file location
CONFIG_FILE = Path.home() / ".google-photos-matcher.json"

# Allow override via environment variable
if os.environ.get("GPM_CONFIG_FILE"):
    CONFIG_FILE = Path(os.environ["GPM_CONFIG_FILE"])


@dataclass
class Config:
    """Application configuration."""
    edited_suffix: str = "editado"
    output_folder: str = "MatchedMedia"
    raw_folder: str = "EditedRaw"
    last_path: Optional[str] = None
    log_level: str = "INFO"
    log_file: Optional[str] = None
    workers: int = 0  # 0 = auto-detect, 1 = sequential, >1 = parallel with N workers

    @classmethod
    def load(cls) -> Config:
        """Load configuration from file, or return defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                # Filter out unknown keys for forward compatibility
                known_fields = {f.name for f in cls.__dataclass_fields__.values()}
                filtered_data = {k: v for k, v in data.items() if k in known_fields}
                return cls(**filtered_data)
            except (json.JSONDecodeError, TypeError, KeyError):
                # Invalid config, return defaults
                return cls()
        return cls()

    def save(self) -> None:
        """Save configuration to file."""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def reset(cls) -> Config:
        """Delete config file and return defaults."""
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        return cls()


def get_config() -> Config:
    """Get the current configuration (singleton pattern)."""
    return Config.load()
