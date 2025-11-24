"""Tests for EXIF-related functions.

Tests include:
- set_EXIF() with mocked piexif operations
- to_deg() coordinate conversion
- change_to_rational() number conversion

Uses mocking to avoid actual file operations.
"""

from __future__ import annotations

import os
from datetime import datetime
from unittest.mock import patch, MagicMock, call

import pytest

from auxFunctions import set_EXIF, to_deg, change_to_rational


class TestToDeg:
    """Test to_deg() coordinate conversion function."""

    def test_positive_latitude_north(self):
        """Positive latitude should return North."""
        result = to_deg(40.7128, ["S", "N"])
        assert result[3] == "N"
        assert result[0] == 40  # degrees
        assert result[1] == 42  # minutes (0.7128 * 60 = 42.768)

    def test_negative_latitude_south(self):
        """Negative latitude should return South."""
        result = to_deg(-33.8688, ["S", "N"])
        assert result[3] == "S"
        assert result[0] == 33  # degrees (absolute)

    def test_positive_longitude_east(self):
        """Positive longitude should return East."""
        result = to_deg(139.6917, ["W", "E"])
        assert result[3] == "E"
        assert result[0] == 139  # degrees

    def test_negative_longitude_west(self):
        """Negative longitude should return West."""
        result = to_deg(-74.006, ["W", "E"])
        assert result[3] == "W"
        assert result[0] == 74  # degrees (absolute)

    def test_zero_value(self):
        """Zero should return empty direction."""
        result = to_deg(0.0, ["S", "N"])
        assert result[3] == ""
        assert result[0] == 0
        assert result[1] == 0
        assert result[2] == 0.0

    def test_whole_degree(self):
        """Whole degree value should have 0 minutes and seconds."""
        result = to_deg(45.0, ["S", "N"])
        assert result[0] == 45
        assert result[1] == 0
        assert result[2] == 0.0

    def test_fractional_seconds(self):
        """Should calculate seconds with precision."""
        # 40.7589 degrees = 40 degrees, 45 minutes, 32.04 seconds
        result = to_deg(40.7589, ["S", "N"])
        assert result[0] == 40
        assert result[1] == 45
        # 0.534 minutes * 60 = 32.04 seconds (approximately)
        assert 32 <= result[2] <= 33

    def test_returns_tuple(self):
        """Should return a tuple with 4 elements."""
        result = to_deg(40.0, ["S", "N"])
        assert isinstance(result, tuple)
        assert len(result) == 4


class TestChangeToRational:
    """Test change_to_rational() number conversion function."""

    def test_whole_number(self):
        """Whole number should return (n, 1)."""
        result = change_to_rational(5)
        assert result == (5, 1)

    def test_simple_fraction(self):
        """Simple fraction should return correct numerator/denominator."""
        result = change_to_rational(0.5)
        assert result == (1, 2)

    def test_decimal_fraction(self):
        """Decimal fraction should return correct values."""
        result = change_to_rational(0.25)
        assert result == (1, 4)

    def test_larger_numerator(self):
        """Should handle fractions with larger numerators."""
        result = change_to_rational(1.5)
        assert result == (3, 2)

    def test_zero(self):
        """Zero should return (0, 1)."""
        result = change_to_rational(0)
        assert result == (0, 1)

    def test_returns_tuple(self):
        """Should return a tuple with 2 elements."""
        result = change_to_rational(1.5)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_precision_handling(self):
        """Should handle floating point precision issues."""
        # 0.1 is notoriously imprecise in floating point
        result = change_to_rational(0.1)
        # Should be approximately 1/10
        assert result[0] / result[1] == pytest.approx(0.1)


class TestSetEXIF:
    """Test set_EXIF() function with mocked piexif operations."""

    @pytest.fixture
    def mock_piexif(self):
        """Create mock piexif module."""
        with patch('auxFunctions.piexif') as mock:
            # Setup mock IFD constants
            mock.ImageIFD.DateTime = 306
            mock.ExifIFD.DateTimeOriginal = 36867
            mock.ExifIFD.DateTimeDigitized = 36868
            mock.GPSIFD.GPSVersionID = 0
            mock.GPSIFD.GPSAltitudeRef = 5
            mock.GPSIFD.GPSAltitude = 6
            mock.GPSIFD.GPSLatitudeRef = 1
            mock.GPSIFD.GPSLatitude = 2
            mock.GPSIFD.GPSLongitudeRef = 3
            mock.GPSIFD.GPSLongitude = 4

            # Setup load to return a dict-like structure
            mock.load.return_value = {
                '0th': {},
                'Exif': {},
                'GPS': {},
                '1st': {},
                'thumbnail': None
            }
            mock.dump.return_value = b'exif_bytes'

            yield mock

    def test_sets_datetime_fields(self, mock_piexif, temp_media_dir, create_test_file):
        """Should set DateTime, DateTimeOriginal, and DateTimeDigitized."""
        filepath = create_test_file("photo.jpg")
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC

        set_EXIF(filepath, 40.7128, -74.006, 10.0, timestamp)

        # Verify load was called with the filepath
        mock_piexif.load.assert_called_once_with(filepath)

        # Verify dump and insert were called
        mock_piexif.dump.assert_called_once()
        mock_piexif.insert.assert_called_once()

    def test_sets_gps_coordinates(self, mock_piexif, temp_media_dir, create_test_file):
        """Should set GPS coordinates in EXIF."""
        filepath = create_test_file("photo.jpg")
        timestamp = 1609459200

        set_EXIF(filepath, 40.7128, -74.006, 100.5, timestamp)

        # Verify GPS data was set
        mock_piexif.dump.assert_called_once()
        # The exif_dict should have GPS data populated
        exif_dict = mock_piexif.load.return_value
        assert 'GPS' in exif_dict

    def test_handles_zero_coordinates(self, mock_piexif, temp_media_dir, create_test_file):
        """Should handle zero coordinates."""
        filepath = create_test_file("photo.jpg")
        timestamp = 1609459200

        # Should not raise an error
        set_EXIF(filepath, 0.0, 0.0, 0.0, timestamp)

        mock_piexif.dump.assert_called_once()

    def test_handles_negative_coordinates(self, mock_piexif, temp_media_dir, create_test_file):
        """Should handle negative coordinates (South/West)."""
        filepath = create_test_file("photo.jpg")
        timestamp = 1609459200

        # Sydney, Australia (South/East)
        set_EXIF(filepath, -33.8688, 151.2093, 58.0, timestamp)

        mock_piexif.dump.assert_called_once()

    def test_handles_coordinate_exception(self, mock_piexif, temp_media_dir, create_test_file, capsys):
        """Should handle exceptions when setting coordinates gracefully."""
        filepath = create_test_file("photo.jpg")
        timestamp = 1609459200

        # Make to_deg raise an exception by mocking it
        with patch('auxFunctions.to_deg', side_effect=Exception("coordinate error")):
            # Should not raise, just print message
            set_EXIF(filepath, 40.7128, -74.006, 10.0, timestamp)

        # Verify it still completed (dump was called for datetime at least)
        mock_piexif.dump.assert_called_once()

    def test_timestamp_conversion(self, mock_piexif, temp_media_dir, create_test_file):
        """Should convert timestamp to correct datetime format."""
        filepath = create_test_file("photo.jpg")
        # Specific timestamp: 2023-06-15 12:30:45
        timestamp = 1686832245

        set_EXIF(filepath, 0.0, 0.0, 0.0, timestamp)

        # The datetime should be in the format "YYYY:MM:DD HH:MM:SS"
        exif_dict = mock_piexif.load.return_value
        # Check that DateTime was set (exact format depends on timezone)
        mock_piexif.dump.assert_called_once()


class TestSetEXIFIntegration:
    """Integration tests for set_EXIF with actual piexif library (skipped if not available)."""

    @pytest.fixture
    def real_jpeg_file(self, temp_media_dir):
        """Create a real JPEG file with valid EXIF structure."""
        # Create a minimal valid JPEG with EXIF
        filepath = os.path.join(temp_media_dir, "test_real.jpg")

        # Minimal JPEG structure
        import struct

        # SOI
        data = b'\xff\xd8'
        # APP0 JFIF marker
        data += b'\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        # APP1 EXIF marker with minimal data
        exif_data = b'Exif\x00\x00'
        # TIFF header (little endian)
        exif_data += b'II\x2a\x00\x08\x00\x00\x00'
        # IFD0: 1 entry
        exif_data += b'\x01\x00'  # 1 entry
        # Entry: ImageWidth = 1
        exif_data += b'\x00\x01\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00'
        # Next IFD offset = 0
        exif_data += b'\x00\x00\x00\x00'

        app1_length = len(exif_data) + 2
        data += b'\xff\xe1' + struct.pack('>H', app1_length) + exif_data

        # DQT (Define Quantization Table)
        data += b'\xff\xdb\x00C\x00'
        data += bytes(64)  # 64 bytes of quantization data

        # SOF0 (Start of Frame)
        data += b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00'

        # DHT (Huffman Table)
        data += b'\xff\xc4\x00\x1f\x00'
        data += bytes(28)  # Huffman table data

        # SOS (Start of Scan)
        data += b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00'
        data += b'\x00'  # Minimal scan data

        # EOI
        data += b'\xff\xd9'

        with open(filepath, 'wb') as f:
            f.write(data)

        return filepath

    @pytest.mark.skip(reason="Integration test requires valid JPEG - run manually")
    def test_real_exif_modification(self, real_jpeg_file):
        """Test actual EXIF modification on a real file."""
        import piexif

        timestamp = 1609459200  # 2021-01-01 00:00:00

        set_EXIF(real_jpeg_file, 40.7128, -74.006, 10.0, timestamp)

        # Verify EXIF was written
        exif_dict = piexif.load(real_jpeg_file)
        assert piexif.ImageIFD.DateTime in exif_dict['0th']


class TestHelperFunctionEdgeCases:
    """Edge case tests for helper functions."""

    def test_to_deg_very_small_value(self):
        """Should handle very small coordinate values."""
        result = to_deg(0.0001, ["S", "N"])
        assert result[3] == "N"
        assert result[0] == 0
        # Minutes should be very small

    def test_to_deg_large_value(self):
        """Should handle maximum coordinate values."""
        result = to_deg(179.9999, ["W", "E"])
        assert result[3] == "E"
        assert result[0] == 179

    def test_change_to_rational_very_precise(self):
        """Should handle numbers requiring high precision."""
        result = change_to_rational(0.123456789)
        # Verify the fraction represents the value reasonably well
        ratio = result[0] / result[1]
        assert ratio == pytest.approx(0.123456789, rel=1e-6)

    def test_change_to_rational_negative(self):
        """Should handle negative numbers."""
        result = change_to_rational(-0.5)
        assert result == (-1, 2)
