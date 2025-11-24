"""Video metadata handling using ffmpeg."""
from __future__ import annotations

import subprocess
import os
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger("GooglePhotosMatcher")


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg is installed and accessible."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def set_video_metadata(
    filepath: str,
    timestamp: int,
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> bool:
    """Set video metadata using ffmpeg.

    Args:
        filepath: Path to video file
        timestamp: Unix timestamp for creation time
        lat: Optional latitude
        lng: Optional longitude

    Returns:
        True if successful, False otherwise
    """
    if not is_ffmpeg_available():
        logger.warning("ffmpeg not available, skipping video metadata")
        return False

    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")

    # Build ffmpeg command
    cmd = [
        "ffmpeg", "-i", filepath,
        "-metadata", f"creation_time={date_str}",
        "-codec", "copy",  # No re-encoding
        "-y",  # Overwrite output
        filepath + ".tmp"
    ]

    # Add location if provided
    if lat is not None and lng is not None:
        location = f"{lat:+.6f}{lng:+.6f}/"
        cmd.insert(-2, "-metadata")
        cmd.insert(-2, f"location={location}")

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        if result.returncode == 0:
            os.replace(filepath + ".tmp", filepath)
            return True
        else:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            # Clean up temp file
            if os.path.exists(filepath + ".tmp"):
                os.remove(filepath + ".tmp")
            return False
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg timeout")
        if os.path.exists(filepath + ".tmp"):
            os.remove(filepath + ".tmp")
        return False
    except Exception as e:
        logger.error(f"Video metadata error: {e}")
        return False
