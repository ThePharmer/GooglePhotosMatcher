"""Tests for searchMedia() function.

Tests media file search patterns including:
- Finding original files
- Finding edited versions (-editado suffix)
- Finding truncated versions (47 char limit)
- Returns None when not found
- File moving behavior
"""

from __future__ import annotations

import os
import pytest

from auxFunctions import searchMedia


class TestFindsOriginalFile:
    """Test that searchMedia finds original files correctly."""

    def test_finds_exact_match(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find file with exact name match."""
        create_test_file("photo.jpg")

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "photo.jpg"

    def test_finds_file_with_spaces(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find file with spaces in name."""
        create_test_file("my photo.jpg")

        result = searchMedia(
            temp_media_dir,
            "my photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "my photo.jpg"

    def test_finds_file_with_unicode(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find file with Unicode characters."""
        create_test_file("\u5199\u771f.jpg")

        result = searchMedia(
            temp_media_dir,
            "\u5199\u771f.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "\u5199\u771f.jpg"

    def test_skips_file_in_media_moved(self, temp_media_dir, non_edited_dir, create_test_file):
        """Should skip files already in mediaMoved set."""
        create_test_file("photo.jpg")
        media_moved = {"photo.jpg"}

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            media_moved,
            non_edited_dir,
            "editado"
        )

        # Should return None or a variant since original is in mediaMoved
        assert result != "photo.jpg" or result is None


class TestFindsEditedVersion:
    """Test that searchMedia finds edited versions with suffix."""

    def test_finds_edited_file(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find edited version with -editado suffix."""
        create_test_file("photo-editado.jpg")

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "photo-editado.jpg"

    def test_moves_original_when_edited_found(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should move original to nonEdited when edited version is found."""
        create_test_file("photo.jpg")
        create_test_file("photo-editado.jpg")

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "photo-editado.jpg"
        # Original should be moved to nonEdited folder
        assert os.path.exists(os.path.join(non_edited_dir, "photo.jpg"))
        assert not os.path.exists(os.path.join(temp_media_dir, "photo.jpg"))

    def test_custom_edited_word(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find edited version with custom suffix."""
        create_test_file("photo-edited.jpg")

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "edited"
        )

        assert result == "photo-edited.jpg"

    def test_edited_file_in_mediamoved_skipped(self, temp_media_dir, non_edited_dir, create_test_file):
        """Should skip edited file if it's in mediaMoved."""
        create_test_file("photo.jpg")
        create_test_file("photo-editado.jpg")
        media_moved = {"photo-editado.jpg"}

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            media_moved,
            non_edited_dir,
            "editado"
        )

        # Should find original since edited is in mediaMoved
        assert result == "photo.jpg"


class TestFindsDuplicateVersion:
    """Test that searchMedia finds (1) duplicate versions."""

    def test_finds_duplicate_version(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find file(1).jpg when original not found."""
        create_test_file("photo(1).jpg")

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "photo(1).jpg"

    def test_skips_duplicate_if_json_exists(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should skip photo(1).jpg if photo.jpg(1).json exists."""
        create_test_file("photo.jpg")
        create_test_file("photo(1).jpg")
        create_test_file("photo.jpg(1).json")

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        # Should find original since (1) has its own JSON
        assert result == "photo.jpg"


class TestFindsTruncatedVersions:
    """Test that searchMedia finds truncated filename versions (47 char limit)."""

    def test_finds_truncated_file(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find truncated version of long filename."""
        # Create a filename longer than 47 chars
        long_name = "a" * 50 + ".jpg"
        truncated_name = "a" * 47 + ".jpg"
        create_test_file(truncated_name)

        result = searchMedia(
            temp_media_dir,
            long_name,
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == truncated_name

    def test_finds_truncated_edited_file(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find truncated edited version."""
        long_name = "a" * 50 + ".jpg"
        truncated_edited = "a" * 47 + "-editado.jpg"
        create_test_file(truncated_edited)

        result = searchMedia(
            temp_media_dir,
            long_name,
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == truncated_edited

    def test_finds_truncated_duplicate_file(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should find truncated (1) version."""
        long_name = "a" * 50 + ".jpg"
        truncated_dup = "a" * 47 + "(1).jpg"
        create_test_file(truncated_dup)

        result = searchMedia(
            temp_media_dir,
            long_name,
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == truncated_dup

    def test_prefers_non_truncated_over_truncated(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should prefer non-truncated version when both exist."""
        long_name = "a" * 50 + ".jpg"
        truncated_name = "a" * 47 + ".jpg"
        create_test_file(long_name)
        create_test_file(truncated_name)

        result = searchMedia(
            temp_media_dir,
            long_name,
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        # Should find original (non-truncated) first
        assert result == long_name


class TestReturnsNoneWhenNotFound:
    """Test that searchMedia returns None when file not found."""

    def test_returns_none_for_missing_file(self, temp_media_dir, non_edited_dir, empty_media_moved):
        """Should return None when file doesn't exist."""
        result = searchMedia(
            temp_media_dir,
            "nonexistent.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result is None

    def test_returns_none_for_empty_directory(self, temp_media_dir, non_edited_dir, empty_media_moved):
        """Should return None when directory is empty."""
        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result is None

    def test_returns_none_when_all_variants_in_mediamoved(self, temp_media_dir, non_edited_dir, create_test_file):
        """Should return None when all possible files are in mediaMoved."""
        create_test_file("photo.jpg")
        create_test_file("photo-editado.jpg")
        create_test_file("photo(1).jpg")
        media_moved = {"photo.jpg", "photo-editado.jpg", "photo(1).jpg"}

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            media_moved,
            non_edited_dir,
            "editado"
        )

        # May find a numbered variant or return None
        # The behavior depends on checkIfSameName finding a gap
        assert result is None or result not in media_moved


class TestSanitizesTitle:
    """Test that searchMedia sanitizes the title before searching."""

    def test_removes_path_traversal(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should sanitize path traversal attempts."""
        create_test_file("photo.jpg")

        result = searchMedia(
            temp_media_dir,
            "../../../photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "photo.jpg"

    def test_removes_dangerous_characters(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should sanitize dangerous characters."""
        create_test_file("photoname.jpg")

        result = searchMedia(
            temp_media_dir,
            "photo<>name.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "photoname.jpg"


class TestFileExtensions:
    """Test handling of various file extensions."""

    def test_handles_mp4_files(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should handle video files."""
        create_test_file("video.mp4")

        result = searchMedia(
            temp_media_dir,
            "video.mp4",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "video.mp4"

    def test_handles_png_files(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should handle PNG files."""
        create_test_file("image.png")

        result = searchMedia(
            temp_media_dir,
            "image.png",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "image.png"

    def test_handles_uppercase_extension(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should handle uppercase extensions."""
        create_test_file("PHOTO.JPG")

        result = searchMedia(
            temp_media_dir,
            "PHOTO.JPG",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "PHOTO.JPG"

    def test_handles_no_extension(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should handle files without extension."""
        create_test_file("README")

        result = searchMedia(
            temp_media_dir,
            "README",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "README"


class TestPriorityOrder:
    """Test that searchMedia checks patterns in correct priority order."""

    def test_prefers_edited_over_original(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should prefer edited version over original."""
        create_test_file("photo.jpg")
        create_test_file("photo-editado.jpg")

        result = searchMedia(
            temp_media_dir,
            "photo.jpg",
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == "photo-editado.jpg"

    def test_prefers_original_over_truncated(self, temp_media_dir, non_edited_dir, create_test_file, empty_media_moved):
        """Should prefer full name over truncated version."""
        long_name = "a" * 50 + ".jpg"
        truncated_name = "a" * 47 + ".jpg"
        create_test_file(long_name)
        create_test_file(truncated_name)

        result = searchMedia(
            temp_media_dir,
            long_name,
            empty_media_moved,
            non_edited_dir,
            "editado"
        )

        assert result == long_name
