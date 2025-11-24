"""Tests for checkIfSameName() function.

Tests unique filename generation including:
- Returns original when not in set
- Increments correctly with (1), (2), etc.
- Raises ValueError at max_attempts
- Edge cases with extensions
"""

from __future__ import annotations

import pytest

from auxFunctions import checkIfSameName


class TestReturnsOriginalWhenNotInSet:
    """Test that original filename is returned when not in mediaMoved set."""

    def test_empty_set_returns_original(self, empty_media_moved):
        """Empty set should return original filename."""
        result = checkIfSameName("photo.jpg", empty_media_moved)
        assert result == "photo.jpg"

    def test_different_file_returns_original(self, sample_media_moved):
        """Different filename not in set should return original."""
        result = checkIfSameName("unique_photo.jpg", sample_media_moved)
        assert result == "unique_photo.jpg"

    def test_similar_but_different_returns_original(self):
        """Similar but different filename should return original."""
        media_moved = {"photo.png"}  # Different extension
        result = checkIfSameName("photo.jpg", media_moved)
        assert result == "photo.jpg"


class TestIncrementsCorrectly:
    """Test that filenames increment correctly with (1), (2), etc."""

    def test_first_duplicate_adds_one(self):
        """First duplicate should add (1)."""
        media_moved = {"file.jpg"}
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(1).jpg"

    def test_second_duplicate_adds_two(self):
        """Second duplicate should add (2)."""
        media_moved = {"file.jpg", "file(1).jpg"}
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(2).jpg"

    def test_third_duplicate_adds_three(self):
        """Third duplicate should add (3)."""
        media_moved = {"file.jpg", "file(1).jpg", "file(2).jpg"}
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(3).jpg"

    def test_skips_existing_numbers(self):
        """Should skip existing numbered variants."""
        media_moved = {"file.jpg", "file(1).jpg", "file(3).jpg"}
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(2).jpg"  # (2) is available

    def test_handles_gaps_in_sequence(self):
        """Should find first available number in gaps."""
        media_moved = {"file.jpg", "file(2).jpg", "file(5).jpg"}
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(1).jpg"  # First gap

    def test_handles_many_duplicates(self):
        """Should handle many duplicates correctly."""
        media_moved = {f"file({i}).jpg" for i in range(100)}
        media_moved.add("file.jpg")
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(100).jpg"


class TestRaisesValueErrorAtMaxAttempts:
    """Test that ValueError is raised when max_attempts is exceeded."""

    def test_raises_at_default_max_attempts(self):
        """Should raise ValueError at default max_attempts (1000)."""
        media_moved = {f"file({i}).jpg" for i in range(1001)}
        media_moved.add("file.jpg")

        with pytest.raises(ValueError) as exc_info:
            checkIfSameName("file.jpg", media_moved)

        assert "Could not find unique name" in str(exc_info.value)
        assert "file.jpg" in str(exc_info.value)
        assert "1000" in str(exc_info.value)

    def test_raises_at_custom_max_attempts(self):
        """Should raise ValueError at custom max_attempts."""
        media_moved = {"file.jpg", "file(1).jpg", "file(2).jpg"}

        with pytest.raises(ValueError) as exc_info:
            checkIfSameName("file.jpg", media_moved, max_attempts=2)

        assert "Could not find unique name" in str(exc_info.value)
        assert "2 attempts" in str(exc_info.value)

    def test_succeeds_just_before_max(self):
        """Should succeed if unique name found just before max."""
        media_moved = {"file.jpg", "file(1).jpg"}
        # max_attempts=2 means try (1) and (2), (2) is available
        result = checkIfSameName("file.jpg", media_moved, max_attempts=2)
        assert result == "file(2).jpg"

    def test_small_max_attempts(self):
        """Should respect small max_attempts value."""
        media_moved = {"file.jpg", "file(1).jpg"}

        with pytest.raises(ValueError):
            checkIfSameName("file.jpg", media_moved, max_attempts=1)


class TestExtensionHandling:
    """Test handling of various file extensions."""

    def test_handles_uppercase_extension(self):
        """Should handle uppercase extensions."""
        media_moved = {"PHOTO.JPG"}
        result = checkIfSameName("PHOTO.JPG", media_moved)
        assert result == "PHOTO(1).JPG"

    def test_handles_double_extension(self):
        """Should handle double extensions like .tar.gz."""
        media_moved = {"archive.tar.gz"}
        result = checkIfSameName("archive.tar.gz", media_moved)
        # Note: function splits on last dot, so this becomes archive.tar(1).gz
        assert result == "archive.tar(1).gz"

    def test_handles_no_extension(self):
        """Should handle files without extension."""
        media_moved = {"README"}
        result = checkIfSameName("README", media_moved)
        assert result == "README(1)"

    def test_handles_dotfile(self):
        """Should handle dotfiles."""
        media_moved = {".gitignore"}
        result = checkIfSameName(".gitignore", media_moved)
        # The function splits on last dot, so this becomes (1).gitignore
        # Actually, let's check the actual behavior
        assert "(1)" in result

    def test_handles_long_extension(self):
        """Should handle long extensions."""
        media_moved = {"document.jpeg"}
        result = checkIfSameName("document.jpeg", media_moved)
        assert result == "document(1).jpeg"


class TestSpecialFilenames:
    """Test special filename cases."""

    def test_filename_with_parentheses_in_name(self):
        """Should handle filenames that already have parentheses."""
        media_moved = {"photo(vacation).jpg"}
        result = checkIfSameName("photo(vacation).jpg", media_moved)
        assert result == "photo(vacation)(1).jpg"

    def test_filename_with_spaces(self):
        """Should handle filenames with spaces."""
        media_moved = {"my photo.jpg"}
        result = checkIfSameName("my photo.jpg", media_moved)
        assert result == "my photo(1).jpg"

    def test_filename_with_unicode(self):
        """Should handle filenames with Unicode characters."""
        media_moved = {"\u5199\u771f.jpg"}
        result = checkIfSameName("\u5199\u771f.jpg", media_moved)
        assert result == "\u5199\u771f(1).jpg"

    def test_filename_with_hyphens(self):
        """Should handle filenames with hyphens."""
        media_moved = {"photo-2023-01-01.jpg"}
        result = checkIfSameName("photo-2023-01-01.jpg", media_moved)
        assert result == "photo-2023-01-01(1).jpg"

    def test_filename_with_underscores(self):
        """Should handle filenames with underscores."""
        media_moved = {"photo_2023_01_01.jpg"}
        result = checkIfSameName("photo_2023_01_01.jpg", media_moved)
        assert result == "photo_2023_01_01(1).jpg"


class TestSetTypes:
    """Test behavior with different set types and contents."""

    def test_works_with_frozenset(self):
        """Should work with frozenset."""
        media_moved = frozenset({"file.jpg"})
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(1).jpg"

    def test_works_with_list_converted_to_set(self):
        """Should work with list converted to set."""
        media_moved = set(["file.jpg", "file(1).jpg"])
        result = checkIfSameName("file.jpg", media_moved)
        assert result == "file(2).jpg"

    def test_case_sensitive_matching(self):
        """Set matching should be case-sensitive."""
        media_moved = {"FILE.JPG"}
        result = checkIfSameName("file.jpg", media_moved)
        # Different case, so original should be returned
        assert result == "file.jpg"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_filename(self):
        """Should handle empty filename."""
        media_moved = {""}
        result = checkIfSameName("", media_moved)
        assert result == "(1)"

    def test_very_long_filename(self):
        """Should handle very long filenames."""
        long_name = "a" * 200 + ".jpg"
        media_moved = {long_name}
        result = checkIfSameName(long_name, media_moved)
        assert result == "a" * 200 + "(1).jpg"

    def test_max_attempts_zero_returns_original_if_available(self):
        """With max_attempts=0, should still return original if not in set."""
        media_moved = {"other.jpg"}
        # max_attempts=0 means no variants tried, but original still works
        result = checkIfSameName("file.jpg", media_moved, max_attempts=0)
        assert result == "file.jpg"

    def test_max_attempts_zero_raises_if_original_taken(self):
        """With max_attempts=0, should raise if original in set."""
        media_moved = {"file.jpg"}
        with pytest.raises(ValueError):
            checkIfSameName("file.jpg", media_moved, max_attempts=0)
