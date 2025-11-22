---
id: 022
priority: p3
status: pending
category: feature
created: 2025-11-22
effort: large
agents: architecture-strategist, kieran-python-reviewer
---

# Add Video and Extended Image Format Support

## Problem Statement

The application only handles common image formats (JPG, TIFF). Users with:
- iPhone photos (HEIC/HEIF)
- Videos (MP4, MOV)
- RAW camera files (CR2, NEF, ARW)

cannot process their full Google Takeout exports.

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py`
- `/home/user/GooglePhotosMatcher/files/auxFunctions.py`
- `/home/user/GooglePhotosMatcher/requirements.txt`

## Proposed Solution

### 1. Video Metadata Support

```python
# New file: files/video_metadata.py
from datetime import datetime
import subprocess
import json

def set_video_metadata(filepath: str, timestamp: int, lat: float, lng: float) -> bool:
    """Set video metadata using ffmpeg."""
    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")

    cmd = [
        "ffmpeg", "-i", filepath,
        "-metadata", f"creation_time={date_str}",
        "-metadata", f"location={lat:+.6f}{lng:+.6f}/",
        "-codec", "copy",
        "-y", filepath + ".tmp"
    ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0:
        os.replace(filepath + ".tmp", filepath)
        return True
    return False
```

### 2. HEIC Support

```python
# Using pillow-heif
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

# Now Image.open() handles HEIC files
with Image.open("photo.heic") as im:
    # Can convert to JPEG if needed
    im.save("photo.jpg", "JPEG")
```

### 3. RAW Support

```python
# Using rawpy for RAW files
import rawpy

def extract_raw_thumbnail(filepath: str) -> Image:
    with rawpy.imread(filepath) as raw:
        thumb = raw.extract_thumb()
        if thumb.format == rawpy.ThumbFormat.JPEG:
            return Image.open(io.BytesIO(thumb.data))
```

### Updated Format Support

| Format | Library | EXIF Support |
|--------|---------|--------------|
| JPEG/TIFF | Pillow + piexif | Full |
| HEIC/HEIF | pillow-heif | Full |
| MP4/MOV | ffmpeg (subprocess) | Via metadata |
| CR2/NEF/ARW | rawpy | Read-only |

## Impact

- Incomplete Takeout processing
- Manual handling of videos
- iPhone users cannot use tool effectively

## Acceptance Criteria

- [ ] HEIC files processed without conversion
- [ ] MP4/MOV timestamps set correctly
- [ ] RAW files copied with correct timestamps (file system level)
- [ ] Graceful fallback if ffmpeg not installed
- [ ] New dependencies documented in README
