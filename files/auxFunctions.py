from __future__ import annotations

import logging
import os
import platform
import time
from datetime import datetime
from typing import Optional

import piexif
from fractions import Fraction

# Get logger (initialized in main.py via setup_logging)
logger = logging.getLogger("GooglePhotosMatcher")

# Only import on Windows
if platform.system() == "Windows":
    from win32_setctime import setctime

# Public API
__all__ = [
    'searchMedia',
    'fixTitle',
    'checkIfSameName',
    'createFolders',
    'set_file_times',
    'set_EXIF',
]


def searchMedia(
    path: str,
    title: str,
    mediaMoved: set[str],
    nonEdited: str,
    editedWord: str
) -> Optional[str]:
    """Search for media file associated with JSON metadata.

    Tries multiple filename patterns in priority order.
    Returns the found filename or None if not found.
    """
    title = fixTitle(title)
    base, ext = title.rsplit('.', 1) if '.' in title else (title, '')
    ext = '.' + ext if ext else ''

    # Define search patterns in priority order
    candidates = [
        f"{base}-{editedWord}{ext}",      # Edited version (e.g., photo-edited.jpg)
        f"{base}(1){ext}",                 # Duplicate naming (e.g., photo(1).jpg)
        title,                             # Original name
    ]

    # Also try truncated versions (Google Photos limits to 47 chars)
    truncated_base = base[:47]
    if truncated_base != base:
        candidates.extend([
            f"{truncated_base}-{editedWord}{ext}",  # Truncated + edited
            f"{truncated_base}(1){ext}",            # Truncated + duplicate
            f"{truncated_base}{ext}",               # Truncated original
        ])

    # Check for edited version - if found, move original to nonEdited folder
    edited_candidate = f"{base}-{editedWord}{ext}"
    edited_path = os.path.join(path, edited_candidate)
    if os.path.exists(edited_path) and edited_candidate not in mediaMoved:
        # Move original to nonEdited folder
        original_path = os.path.join(path, title)
        if os.path.exists(original_path):
            os.replace(original_path, os.path.join(nonEdited, title))
        return edited_candidate

    # Check duplicate (1) version
    dup_candidate = f"{base}(1){ext}"
    dup_path = os.path.join(path, dup_candidate)
    dup_json_path = os.path.join(path, f"{title}(1).json")
    if os.path.exists(dup_path) and not os.path.exists(dup_json_path) and dup_candidate not in mediaMoved:
        original_path = os.path.join(path, title)
        if os.path.exists(original_path):
            os.replace(original_path, os.path.join(nonEdited, title))
        return dup_candidate

    # Check original name
    if os.path.exists(os.path.join(path, title)) and title not in mediaMoved:
        return title

    # Check with checkIfSameName for numbered variants
    variant = checkIfSameName(title, mediaMoved)
    if os.path.exists(os.path.join(path, variant)):
        return variant

    # Try truncated versions
    if truncated_base != base:
        truncated_title = f"{truncated_base}{ext}"
        for candidate in [f"{truncated_base}-{editedWord}{ext}", f"{truncated_base}(1){ext}", truncated_title]:
            candidate_path = os.path.join(path, candidate)
            if os.path.exists(candidate_path) and candidate not in mediaMoved:
                if candidate != truncated_title:
                    original_path = os.path.join(path, truncated_title)
                    if os.path.exists(original_path):
                        os.replace(original_path, os.path.join(nonEdited, truncated_title))
                return candidate

        # Check truncated with checkIfSameName
        variant = checkIfSameName(truncated_title, mediaMoved)
        if os.path.exists(os.path.join(path, variant)):
            return variant

    return None


def fixTitle(title: str) -> str:
    """Sanitize title by removing path components and dangerous characters."""
    # Get only the basename, removing any path components (security: prevent path traversal)
    title = os.path.basename(str(title))
    # Remove dangerous characters
    dangerous_chars = ['%', '<', '>', '=', ':', '?', '¿', '*', '#', '&',
                       '{', '}', '\\', '@', '!', '+', '|', '"', "'", '\x00']
    for char in dangerous_chars:
        title = title.replace(char, "")
    return title

def checkIfSameName(title: str, mediaMoved: set[str], max_attempts: int = 1000) -> str:
    """Find unique filename by appending (1), (2), etc.

    Args:
        title: Original filename
        mediaMoved: Set of already used filenames
        max_attempts: Maximum number of variants to try

    Returns:
        A unique filename not in mediaMoved

    Raises:
        ValueError: If no unique name found within max_attempts
    """
    if title not in mediaMoved:
        return title

    base, ext = title.rsplit('.', 1) if '.' in title else (title, '')
    ext = '.' + ext if ext else ''

    for i in range(1, max_attempts + 1):
        candidate = f"{base}({i}){ext}"
        if candidate not in mediaMoved:
            return candidate

    raise ValueError(f"Could not find unique name for {title} after {max_attempts} attempts")

def createFolders(fixed: str, nonEdited: str) -> None:
    if not os.path.exists(fixed):
        os.mkdir(fixed)

    if not os.path.exists(nonEdited):
        os.mkdir(nonEdited)

def set_file_times(filepath: str, timestamp: int) -> None:
    """Set file creation and modification times cross-platform."""

    # Set modification time (works on all platforms)
    date = datetime.fromtimestamp(timestamp)
    mod_time = time.mktime(date.timetuple())
    os.utime(filepath, (mod_time, mod_time))

    # Set creation time (platform-specific)
    system = platform.system()

    if system == "Windows":
        from win32_setctime import setctime
        setctime(filepath, timestamp)
    elif system == "Darwin":  # macOS
        try:
            import subprocess
            date_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y %H:%M:%S")
            subprocess.run(["SetFile", "-d", date_str, filepath], check=False, capture_output=True)
        except Exception:
            pass  # SetFile not available, modification time already set
    # Linux: creation time not typically supported, modification time already set

def to_deg(value: float, loc: list[str]) -> tuple[int, int, float, str]:
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number: float) -> tuple[int, int]:
    """convert a number to rational
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def set_EXIF(filepath: str, lat: float, lng: float, altitude: float, timeStamp: int) -> None:
    exif_dict = piexif.load(filepath)

    dateTime = datetime.fromtimestamp(timeStamp).strftime("%Y:%m:%d %H:%M:%S")  # Create date object
    exif_dict['0th'][piexif.ImageIFD.DateTime] = dateTime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dateTime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = dateTime

    try:
        lat_deg = to_deg(lat, ["S", "N"])
        lng_deg = to_deg(lng, ["W", "E"])

        exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
        exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSAltitudeRef: 1,
            piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude, 2)),
            piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
            piexif.GPSIFD.GPSLatitude: exiv_lat,
            piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
            piexif.GPSIFD.GPSLongitude: exiv_lng,
        }

        exif_dict['GPS'] = gps_ifd

    except Exception as e:
        logger.warning(f"Coordinates not settled: {e}")

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filepath)


