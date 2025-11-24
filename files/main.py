from __future__ import annotations

import os
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Protocol, TYPE_CHECKING

from PIL import Image
from auxFunctions import (
    searchMedia,
    createFolders,
    set_file_times,
    set_EXIF,
)
from logger import setup_logging
from video_metadata import set_video_metadata, is_ffmpeg_available

# Optional PySimpleGUI import for type checking only
if TYPE_CHECKING:
    import PySimpleGUI as sg


def _get_default_workers() -> int:
    """Get sensible default number of workers based on CPU count."""
    cpu_count = os.cpu_count() or 1
    return min(4, cpu_count)


class ProgressWindow(Protocol):
    """Protocol for window objects supporting progress updates.

    This allows both PySimpleGUI windows and CLI mock windows to be used
    interchangeably with mainProcess.
    """

    def __getitem__(self, key: str) -> Any:
        """Get progress element by key."""
        ...


@dataclass
class ProcessResult:
    """Result of processing a single JSON file.

    Attributes:
        filename: Name of the JSON file processed
        success: Whether processing completed successfully
        title: Media file title if found
        error: Error message if processing failed
        operation: Planned operation details for dry-run mode
    """
    filename: str
    success: bool
    title: Optional[str] = None
    error: Optional[str] = None
    operation: Optional[dict[str, Any]] = None


# Initialize logger at module level
logger = setup_logging(level="DEBUG")


def process_single_file(
    entry: os.DirEntry,
    path: str,
    fixedMediaPath: str,
    nonEditedMediaPath: str,
    editedWord: str,
    piexifCodecs: list[str],
    videoCodecs: list[str],
    heicCodecs: list[str],
    rawCodecs: list[str],
    mediaMoved: set[str],
    mediaMoved_lock: threading.Lock,
    dry_run: bool = False,
    ffmpeg_available: bool = False,
    heic_available: bool = False
) -> ProcessResult:
    """Process a single JSON file and its associated media.

    This function is designed to be called from a thread pool.
    Thread safety is ensured by using mediaMoved_lock when accessing
    the shared mediaMoved set and during file search operations.

    Args:
        entry: Directory entry for the JSON file
        path: Source path containing media files
        fixedMediaPath: Destination path for matched media
        nonEditedMediaPath: Path for non-edited originals
        editedWord: Suffix indicating edited versions
        piexifCodecs: List of image formats supporting EXIF
        videoCodecs: List of video formats
        heicCodecs: List of HEIC/HEIF formats
        rawCodecs: List of RAW image formats
        mediaMoved: Set tracking processed media files
        mediaMoved_lock: Lock for thread-safe access to mediaMoved
        dry_run: If True, don't modify files
        ffmpeg_available: Whether ffmpeg is available for video processing
        heic_available: Whether pillow-heif is available

    Returns:
        ProcessResult with success status and details
    """
    try:
        with open(entry, encoding="utf8") as f:
            data = json.load(f)

        # Validate JSON structure
        if 'title' not in data:
            logger.warning(f"Missing 'title' in JSON: {entry.name}")
            return ProcessResult(entry.name, success=False, error="Missing 'title' in JSON")

        titleOriginal = data['title']

        # Thread-safe search for media file
        # searchMedia modifies files and checks mediaMoved, so we need to lock
        with mediaMoved_lock:
            try:
                title = searchMedia(path, titleOriginal, mediaMoved, nonEditedMediaPath, editedWord)
            except Exception as e:
                logger.error(f"Error on searchMedia() with file {titleOriginal}: {e}")
                return ProcessResult(entry.name, success=False, error=f"searchMedia error: {e}")

            if title is None:
                logger.warning(f"{titleOriginal} not found")
                return ProcessResult(entry.name, success=False, error=f"{titleOriginal} not found")

            # Add to mediaMoved while we still hold the lock
            mediaMoved.add(title)

        filepath = os.path.join(path, title)

        # METADATA EDITION
        if 'photoTakenTime' not in data or 'timestamp' not in data.get('photoTakenTime', {}):
            logger.warning(f"Missing timestamp in JSON: {entry.name}")
            return ProcessResult(entry.name, success=False, title=title, error="Missing timestamp in JSON")

        timeStamp = int(data['photoTakenTime']['timestamp'])
        logger.debug(f"Processing file: {filepath}")

        # Determine file extension for format-specific handling
        file_extension = title.rsplit('.', 1)[1].casefold() if '.' in title else ''
        supports_exif = file_extension in piexifCodecs
        is_video = file_extension in videoCodecs
        is_heic = file_extension in heicCodecs
        is_raw = file_extension in rawCodecs

        if dry_run:
            # Track planned operation without modifying files
            operation: dict[str, Any] = {
                "action": "move",
                "source": filepath,
                "destination": os.path.join(fixedMediaPath, title),
                "json_file": entry.name,
                "format_type": "jpeg/tiff" if supports_exif else
                               "video" if is_video else
                               "heic" if is_heic else
                               "raw" if is_raw else "unknown",
            }

            if supports_exif or (is_heic and heic_available):
                operation["exif_changes"] = {
                    "DateTime": datetime.fromtimestamp(timeStamp).strftime("%Y:%m:%d %H:%M:%S"),
                }
                try:
                    operation["gps"] = (data['geoData']['latitude'], data['geoData']['longitude'])
                    operation["altitude"] = data['geoData']['altitude']
                except (KeyError, TypeError):
                    pass

            if is_video and ffmpeg_available:
                operation["video_metadata"] = {
                    "creation_time": datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%dT%H:%M:%S"),
                }
                try:
                    operation["video_metadata"]["location"] = (
                        data['geoData']['latitude'],
                        data['geoData']['longitude']
                    )
                except (KeyError, TypeError):
                    pass

            if is_raw:
                operation["note"] = "RAW file - file times only, no EXIF modification"

            operation["file_times"] = {
                "timestamp": timeStamp,
                "datetime": datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S"),
            }

            logger.debug(f"[DRY-RUN] Would process: {title} (format: {operation['format_type']})")
            return ProcessResult(entry.name, success=True, title=title, operation=operation)

        # Normal mode - actually modify files
        if supports_exif:
            # JPEG/TIFF handling with EXIF
            try:
                with Image.open(filepath) as im:
                    rgb_im = im.convert('RGB')
                    new_filepath = filepath.rsplit('.', 1)[0] + ".jpg"
                    os.replace(filepath, new_filepath)
                    filepath = new_filepath
                    rgb_im.save(filepath)
            except ValueError as e:
                logger.error(f"Error converting to JPG in {title}: {e}")
                return ProcessResult(entry.name, success=False, title=title, error=f"JPG conversion error: {e}")

            try:
                set_EXIF(filepath, data['geoData']['latitude'], data['geoData']['longitude'], data['geoData']['altitude'], timeStamp)
            except Exception as e:
                logger.warning(f"Inexistent EXIF data for {filepath}: {e}")
                # Continue processing - file times will still be set

        elif is_video:
            # Video handling with ffmpeg
            if ffmpeg_available:
                try:
                    lat = data.get('geoData', {}).get('latitude')
                    lng = data.get('geoData', {}).get('longitude')
                    if not set_video_metadata(filepath, timeStamp, lat, lng):
                        logger.warning(f"Could not set video metadata for {title}")
                except Exception as e:
                    logger.warning(f"Could not set video metadata for {title}: {e}")
            else:
                logger.debug(f"Video {title} - ffmpeg not available, setting file times only")

        elif is_heic:
            # HEIC handling (requires pillow-heif)
            if heic_available:
                try:
                    # pillow-heif is already registered, so Image.open works on HEIC
                    with Image.open(filepath) as im:
                        # Convert to JPEG for EXIF modification
                        rgb_im = im.convert('RGB')
                        new_filepath = filepath.rsplit('.', 1)[0] + ".jpg"
                        rgb_im.save(new_filepath)
                        os.remove(filepath)
                        filepath = new_filepath
                        # Update title for the move operation
                        title = os.path.basename(new_filepath)

                    try:
                        set_EXIF(filepath, data['geoData']['latitude'], data['geoData']['longitude'], data['geoData']['altitude'], timeStamp)
                    except Exception as e:
                        logger.warning(f"Inexistent EXIF data for {filepath}: {e}")
                except Exception as e:
                    logger.warning(f"Could not process HEIC {title}: {e}")
            else:
                logger.debug(f"HEIC {title} - pillow-heif not available, setting file times only")

        elif is_raw:
            # RAW files - just set file times, no EXIF modification
            logger.debug(f"RAW file {title} - setting file times only")

        # Always set file creation and modification times (works for all file types)
        set_file_times(filepath, timeStamp)

        # MOVE FILE AND DELETE JSON
        os.replace(filepath, os.path.join(fixedMediaPath, title))
        os.remove(os.path.join(path, entry.name))

        return ProcessResult(entry.name, success=True, title=title)

    except Exception as e:
        logger.error(f"Unexpected error processing {entry.name}: {e}")
        return ProcessResult(entry.name, success=False, error=str(e))


def mainProcess(
    browserPath: str,
    window: ProgressWindow,
    editedW: Optional[str],
    dry_run: bool = False,
    max_workers: int = 0
) -> dict[str, Any]:
    """Process Google Takeout media files with optional parallel execution.

    Args:
        browserPath: Path to Google Takeout folder
        window: Window object for progress updates
        editedW: Suffix for edited photos (e.g., 'editado')
        dry_run: If True, show what would be done without making changes
        max_workers: Number of parallel workers. 0 = auto-detect,
                    1 = sequential, >1 = parallel with N workers

    Returns:
        Dictionary with success_count, error_count, dry_run status, and
        optional operations list (for dry-run mode) or error message
    """
    # Auto-detect workers if not specified
    if max_workers <= 0:
        max_workers = _get_default_workers()

    # Image formats supporting EXIF via piexif
    piexifCodecs = [k.casefold() for k in ['TIF', 'TIFF', 'JPEG', 'JPG']]

    # Video formats (require ffmpeg)
    videoCodecs = [k.casefold() for k in ['MP4', 'MOV', 'AVI', 'MKV', 'M4V']]

    # HEIC support (requires pillow-heif)
    heicCodecs = [k.casefold() for k in ['HEIC', 'HEIF']]

    # RAW formats (file time only, no EXIF modification)
    rawCodecs = [k.casefold() for k in ['CR2', 'NEF', 'ARW', 'DNG', 'RAF', 'ORF']]

    # Check optional dependencies availability
    ffmpeg_available = is_ffmpeg_available()
    if not ffmpeg_available:
        logger.info("ffmpeg not available - video metadata will not be modified")

    heic_available = False
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
        heic_available = True
    except ImportError:
        logger.info("pillow-heif not installed - HEIC EXIF will not be modified")

    # Thread-safe set for tracking processed files
    mediaMoved: set[str] = set()
    mediaMoved_lock = threading.Lock()

    operations: list[dict[str, Any]] = []  # Track planned operations for dry-run mode
    path = browserPath  # source path
    fixedMediaPath = os.path.join(path, "MatchedMedia")  # destination path
    nonEditedMediaPath = os.path.join(path, "EditedRaw")
    editedWord = editedW or "editado"

    logger.debug(f"Using edited word: {editedWord}")
    logger.debug(f"Using {max_workers} worker(s)")

    if dry_run:
        logger.info("Running in dry-run mode - no files will be modified")

    try:
        obj = list(os.scandir(path))
        obj.sort(key=lambda s: len(s.name))  # Sort by length to avoid name(1).jpg be processed before name.jpg
        if not dry_run:
            createFolders(fixedMediaPath, nonEditedMediaPath)
    except Exception as e:
        window['-PROGRESS_LABEL-'].update("Choose a valid directory", visible=True, text_color='red')
        return {"success_count": 0, "error_count": 0, "dry_run": dry_run, "error": str(e)}

    # Filter to only JSON files
    json_files = [e for e in obj if e.is_file() and e.name.endswith(".json")]
    total_files = len(json_files)

    if total_files == 0:
        window['-PROGRESS_LABEL-'].update("No JSON files found", visible=True, text_color='yellow')
        return {"success_count": 0, "error_count": 0, "dry_run": dry_run}

    results: list[ProcessResult] = []

    if max_workers == 1:
        # Sequential processing (original behavior)
        for idx, entry in enumerate(json_files):
            result = process_single_file(
                entry, path, fixedMediaPath, nonEditedMediaPath,
                editedWord, piexifCodecs, videoCodecs, heicCodecs, rawCodecs,
                mediaMoved, mediaMoved_lock, dry_run,
                ffmpeg_available, heic_available
            )
            results.append(result)

            # Update progress
            progress = round((idx + 1) / total_files * 100, 2)
            window['-PROGRESS_LABEL-'].update(str(progress) + "%", visible=True)
            window['-PROGRESS_BAR-'].update(progress, visible=True)
    else:
        # Parallel processing
        completed = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    process_single_file,
                    entry, path, fixedMediaPath, nonEditedMediaPath,
                    editedWord, piexifCodecs, videoCodecs, heicCodecs, rawCodecs,
                    mediaMoved, mediaMoved_lock, dry_run,
                    ffmpeg_available, heic_available
                ): entry
                for entry in json_files
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                completed += 1

                # Update progress
                progress = round(completed / total_files * 100, 2)
                window['-PROGRESS_LABEL-'].update(str(progress) + "%", visible=True)
                window['-PROGRESS_BAR-'].update(progress, visible=True)

    # Count results
    successCounter = sum(1 for r in results if r.success)
    errorCounter = sum(1 for r in results if not r.success)

    # Collect operations for dry-run mode
    if dry_run:
        operations = [r.operation for r in results if r.success and r.operation]

    # Log errors
    for result in results:
        if not result.success and result.error:
            logger.error(f"{result.filename}: {result.error}")

    successMessage = " successes"
    errorMessage = " errors"

    if successCounter == 1:
        successMessage = " success"

    if errorCounter == 1:
        errorMessage = " error"

    window['-PROGRESS_BAR-'].update(100, visible=True)

    if dry_run:
        # Print dry-run summary
        print("\n=== DRY RUN SUMMARY ===")
        print(f"Files to process: {len(operations)}")
        print(f"Files to move: {successCounter}")
        print(f"Files to skip (errors): {errorCounter}")
        print("\nPlanned operations:")
        for op in operations:
            format_type = op.get('format_type', 'unknown')
            print(f"  - Move: {os.path.basename(op['source'])} -> MatchedMedia/ [{format_type}]")
            if 'exif_changes' in op:
                print(f"    EXIF DateTime: {op['exif_changes']['DateTime']}")
                if 'gps' in op:
                    print(f"    GPS: {op['gps']}")
            if 'video_metadata' in op:
                print(f"    Video creation_time: {op['video_metadata']['creation_time']}")
                if 'location' in op['video_metadata']:
                    print(f"    Video location: {op['video_metadata']['location']}")
            if 'note' in op:
                print(f"    Note: {op['note']}")
            if 'file_times' in op:
                print(f"    File time: {op['file_times']['datetime']}")
        print("\nNo files were modified.")
        window['-PROGRESS_LABEL-'].update(
            f"[DRY-RUN] Would process {successCounter}{successMessage} and {errorCounter}{errorMessage}.",
            visible=True,
            text_color='#ffff99'
        )
        return {
            "operations": operations,
            "success_count": successCounter,
            "error_count": errorCounter,
            "dry_run": True
        }

    window['-PROGRESS_LABEL-'].update("Matching process finished with " + str(successCounter) + successMessage + " and " + str(errorCounter) + errorMessage + ".", visible=True, text_color='#c0ffb3')
    return {
        "success_count": successCounter,
        "error_count": errorCounter,
        "dry_run": False
    }
