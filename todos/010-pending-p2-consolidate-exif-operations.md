---
id: 010
priority: p2
status: pending
category: performance
created: 2025-11-22
effort: small
agents: performance-oracle
---

# Consolidate Redundant EXIF Load/Save Operations

## Problem Statement

The `set_EXIF()` function loads EXIF data, saves it, then loads it again for GPS processing - doubling file I/O.

```python
exif_dict = piexif.load(filepath)  # First load
# ... set datetime ...
piexif.insert(exif_bytes, filepath)  # First save

exif_dict = piexif.load(filepath)  # REDUNDANT second load
# ... set GPS ...
piexif.insert(exif_bytes, filepath)  # Second save
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (lines 109-142)

## Proposed Solution

```python
def set_EXIF(filepath, lat, lng, altitude, timeStamp):
    exif_dict = piexif.load(filepath)  # Single load

    # Set datetime
    dateTime = datetime.fromtimestamp(timeStamp).strftime("%Y:%m:%d %H:%M:%S")
    exif_dict['0th'][piexif.ImageIFD.DateTime] = dateTime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dateTime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = dateTime

    # Set GPS in same operation
    try:
        # ... build gps_ifd ...
        exif_dict['GPS'] = gps_ifd
    except Exception:
        pass  # GPS optional

    # Single save
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filepath)
```

## Impact

- 2x unnecessary file I/O per image
- For 5,000 images @ 3MB each: ~30GB wasted I/O

## Acceptance Criteria

- [ ] Single load/save cycle per image
- [ ] GPS failure doesn't prevent datetime save
- [ ] No regression in EXIF data accuracy
