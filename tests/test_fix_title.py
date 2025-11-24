"""Tests for fixTitle() function.

Tests filename sanitization including:
- Path traversal prevention
- Dangerous character removal
- Unicode handling
- Normal filename preservation
"""

from __future__ import annotations

import pytest

from auxFunctions import fixTitle


class TestPathTraversalPrevention:
    """Test that path traversal attempts are blocked."""

    def test_removes_parent_directory_references(self):
        """Path traversal with ../ should return only basename."""
        assert fixTitle("../../../etc/passwd") == "passwd"

    def test_removes_absolute_path_unix(self):
        """Absolute Unix paths should return only basename."""
        assert fixTitle("/etc/passwd") == "passwd"

    def test_removes_nested_path_traversal(self):
        """Deeply nested path traversal should return only basename."""
        assert fixTitle("foo/../bar/../../../secret.txt") == "secret.txt"

    def test_removes_dot_directory(self):
        """Current directory reference should be handled."""
        assert fixTitle("./photo.jpg") == "photo.jpg"

    def test_removes_mixed_separators(self):
        """Mixed path separators should be handled."""
        # os.path.basename handles this based on the platform
        result = fixTitle("folder/subfolder/image.jpg")
        assert result == "image.jpg"


class TestDangerousCharacterRemoval:
    """Test that dangerous characters are removed from filenames."""

    def test_removes_angle_brackets(self):
        """Angle brackets < > should be removed."""
        assert fixTitle("file<name>.jpg") == "filename.jpg"

    def test_removes_percent(self):
        """Percent sign should be removed."""
        assert fixTitle("file%20name.jpg") == "file20name.jpg"

    def test_removes_equals_sign(self):
        """Equals sign should be removed."""
        assert fixTitle("file=name.jpg") == "filename.jpg"

    def test_removes_colon(self):
        """Colon should be removed."""
        assert fixTitle("file:name.jpg") == "filename.jpg"

    def test_removes_question_mark(self):
        """Question mark should be removed."""
        assert fixTitle("file?name.jpg") == "filename.jpg"

    def test_removes_inverted_question_mark(self):
        """Inverted question mark should be removed."""
        assert fixTitle("file\u00bfname.jpg") == "filename.jpg"

    def test_removes_asterisk(self):
        """Asterisk should be removed."""
        assert fixTitle("file*name.jpg") == "filename.jpg"

    def test_removes_hash(self):
        """Hash/pound sign should be removed."""
        assert fixTitle("file#name.jpg") == "filename.jpg"

    def test_removes_ampersand(self):
        """Ampersand should be removed."""
        assert fixTitle("file&name.jpg") == "filename.jpg"

    def test_removes_curly_braces(self):
        """Curly braces should be removed."""
        assert fixTitle("file{name}.jpg") == "filename.jpg"

    def test_removes_backslash(self):
        """Backslash should be removed."""
        assert fixTitle("file\\name.jpg") == "filename.jpg"

    def test_removes_at_sign(self):
        """At sign should be removed."""
        assert fixTitle("file@name.jpg") == "filename.jpg"

    def test_removes_exclamation(self):
        """Exclamation mark should be removed."""
        assert fixTitle("file!name.jpg") == "filename.jpg"

    def test_removes_plus(self):
        """Plus sign should be removed."""
        assert fixTitle("file+name.jpg") == "filename.jpg"

    def test_removes_pipe(self):
        """Pipe character should be removed."""
        assert fixTitle("file|name.jpg") == "filename.jpg"

    def test_removes_double_quote(self):
        """Double quote should be removed."""
        assert fixTitle('file"name.jpg') == "filename.jpg"

    def test_removes_single_quote(self):
        """Single quote should be removed."""
        assert fixTitle("file'name.jpg") == "filename.jpg"

    def test_removes_null_character(self):
        """Null character should be removed."""
        assert fixTitle("file\x00name.jpg") == "filename.jpg"

    def test_removes_multiple_dangerous_chars(self):
        """Multiple dangerous characters should all be removed."""
        assert fixTitle("file<>:*?name.jpg") == "filename.jpg"


class TestUnicodeHandling:
    """Test that Unicode characters are handled correctly."""

    def test_preserves_unicode_letters(self):
        """Unicode letters should be preserved."""
        assert fixTitle("caf\u00e9.jpg") == "caf\u00e9.jpg"

    def test_preserves_japanese_characters(self):
        """Japanese characters should be preserved."""
        assert fixTitle("\u5199\u771f.jpg") == "\u5199\u771f.jpg"

    def test_preserves_emoji(self):
        """Emoji characters should be preserved."""
        assert fixTitle("\U0001f600photo.jpg") == "\U0001f600photo.jpg"

    def test_preserves_accented_characters(self):
        """Accented characters should be preserved."""
        assert fixTitle("\u00e1\u00e9\u00ed\u00f3\u00fa.jpg") == "\u00e1\u00e9\u00ed\u00f3\u00fa.jpg"

    def test_preserves_chinese_characters(self):
        """Chinese characters should be preserved."""
        assert fixTitle("\u4e2d\u6587\u6587\u4ef6.jpg") == "\u4e2d\u6587\u6587\u4ef6.jpg"

    def test_handles_mixed_unicode_and_dangerous(self):
        """Mix of Unicode and dangerous characters should be handled."""
        assert fixTitle("caf\u00e9<test>.jpg") == "caf\u00e9test.jpg"


class TestNormalFilenames:
    """Test that normal, safe filenames are preserved unchanged."""

    def test_preserves_simple_filename(self):
        """Simple filename should be unchanged."""
        assert fixTitle("photo.jpg") == "photo.jpg"

    def test_preserves_filename_with_numbers(self):
        """Filename with numbers should be unchanged."""
        assert fixTitle("photo123.jpg") == "photo123.jpg"

    def test_preserves_filename_with_underscores(self):
        """Filename with underscores should be unchanged."""
        assert fixTitle("photo_2023_01_01.jpg") == "photo_2023_01_01.jpg"

    def test_preserves_filename_with_hyphens(self):
        """Filename with hyphens should be unchanged."""
        assert fixTitle("photo-2023-01-01.jpg") == "photo-2023-01-01.jpg"

    def test_preserves_filename_with_spaces(self):
        """Filename with spaces should be unchanged."""
        assert fixTitle("my photo.jpg") == "my photo.jpg"

    def test_preserves_filename_with_dots(self):
        """Filename with multiple dots should be unchanged."""
        assert fixTitle("photo.backup.jpg") == "photo.backup.jpg"

    def test_preserves_filename_with_parentheses(self):
        """Filename with parentheses should be unchanged."""
        assert fixTitle("photo(1).jpg") == "photo(1).jpg"

    def test_preserves_uppercase_extension(self):
        """Uppercase extension should be unchanged."""
        assert fixTitle("PHOTO.JPG") == "PHOTO.JPG"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert fixTitle("") == ""

    def test_only_dangerous_chars(self):
        """String of only dangerous chars should return empty."""
        assert fixTitle("<>:*?") == ""

    def test_extension_only(self):
        """Extension only should be preserved."""
        assert fixTitle(".jpg") == ".jpg"

    def test_no_extension(self):
        """Filename without extension should be handled."""
        assert fixTitle("filename") == "filename"

    def test_long_filename(self):
        """Long filename should be handled without modification."""
        long_name = "a" * 200 + ".jpg"
        assert fixTitle(long_name) == long_name

    def test_handles_integer_input(self):
        """Integer input should be converted to string."""
        # The function uses str() on input
        assert fixTitle(12345) == "12345"

    def test_preserves_dots_in_middle(self):
        """Multiple dots should be preserved."""
        assert fixTitle("file.name.backup.jpg") == "file.name.backup.jpg"
