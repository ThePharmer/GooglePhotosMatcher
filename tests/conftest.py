"""Shared pytest fixtures for GooglePhotosMatcher tests."""

from __future__ import annotations

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator

import pytest

# Add the files directory to the path so we can import auxFunctions
sys.path.insert(0, str(Path(__file__).parent.parent / "files"))


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests and clean up afterward."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_media_dir(temp_dir: str) -> str:
    """Create a temporary directory structure for media file tests."""
    media_dir = os.path.join(temp_dir, "media")
    non_edited_dir = os.path.join(temp_dir, "nonEdited")
    os.makedirs(media_dir)
    os.makedirs(non_edited_dir)
    return media_dir


@pytest.fixture
def non_edited_dir(temp_dir: str) -> str:
    """Return the non-edited directory path."""
    return os.path.join(temp_dir, "nonEdited")


@pytest.fixture
def empty_media_moved() -> set[str]:
    """Return an empty set for tracking moved media."""
    return set()


@pytest.fixture
def sample_media_moved() -> set[str]:
    """Return a pre-populated set of moved media filenames."""
    return {"photo1.jpg", "photo2.jpg", "video1.mp4"}


@pytest.fixture
def create_test_file(temp_media_dir: str):
    """Factory fixture to create test files in the temp media directory."""
    def _create_file(filename: str, content: bytes = b"test content") -> str:
        filepath = os.path.join(temp_media_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return filepath
    return _create_file


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    """Return minimal valid JPEG bytes for EXIF testing.

    This is a minimal valid JPEG with an APP1 marker for EXIF data.
    """
    # Minimal JPEG with EXIF APP1 marker
    # SOI (Start of Image)
    soi = b'\xff\xd8'
    # APP1 marker with minimal EXIF header
    app1_marker = b'\xff\xe1'
    # EXIF header: "Exif\x00\x00" followed by TIFF header
    exif_header = b'Exif\x00\x00'
    # TIFF header: little endian (II), magic number (42), IFD offset (8)
    tiff_header = b'II\x2a\x00\x08\x00\x00\x00'
    # Minimal IFD0 with 0 entries and no next IFD
    ifd0 = b'\x00\x00\x00\x00\x00\x00'

    exif_data = exif_header + tiff_header + ifd0
    # Length includes the length field itself (2 bytes) + data
    app1_length = len(exif_data) + 2
    app1 = app1_marker + app1_length.to_bytes(2, 'big') + exif_data

    # Minimal scan data
    # SOF0 (Start of Frame)
    sof0 = b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00'
    # DHT (Define Huffman Table) - minimal
    dht = b'\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b'
    # SOS (Start of Scan)
    sos = b'\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\x7f'
    # EOI (End of Image)
    eoi = b'\xff\xd9'

    return soi + app1 + sof0 + dht + sos + eoi


@pytest.fixture
def create_jpeg_file(temp_media_dir: str, sample_jpeg_bytes: bytes):
    """Factory fixture to create test JPEG files."""
    def _create_jpeg(filename: str) -> str:
        filepath = os.path.join(temp_media_dir, filename)
        with open(filepath, "wb") as f:
            f.write(sample_jpeg_bytes)
        return filepath
    return _create_jpeg
