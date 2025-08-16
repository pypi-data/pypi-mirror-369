"""
Tests for utility functions.
"""

from ai_subtitle_translator.utils import generate_mono_output_filename


class TestGenerateMonoOutputFilename:
    """Test the generate_mono_output_filename function."""

    def test_en_zh_pattern(self):
        """Test extraction with .en-zh.ass pattern."""
        input_file = "/path/to/movie.en-zh.ass"
        expected = "/path/to/movie.zh.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_en_fr_pattern(self):
        """Test extraction with .en-fr.ass pattern."""
        input_file = "/path/to/movie.en-fr.ass"
        expected = "/path/to/movie.fr.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_es_pt_pattern(self):
        """Test extraction with .es-pt.ass pattern."""
        input_file = "/path/to/movie.es-pt.ass"
        expected = "/path/to/movie.pt.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_de_it_pattern(self):
        """Test extraction with .de-it.ass pattern."""
        input_file = "/path/to/movie.de-it.ass"
        expected = "/path/to/movie.it.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_case_insensitive_pattern(self):
        """Test extraction with case-insensitive patterns."""
        input_file = "/path/to/movie.EN-ZH.ass"
        expected = "/path/to/movie.zh.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_fallback_to_mono(self):
        """Test fallback to .mono.ass for non-standard patterns."""
        input_file = "/path/to/movie.ass"
        expected = "/path/to/movie.mono.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_fallback_with_long_language_codes(self):
        """Test fallback with longer language codes (not 2 characters)."""
        input_file = "/path/to/movie.english-chinese.ass"
        expected = "/path/to/movie.english-chinese.mono.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_fallback_with_single_language(self):
        """Test fallback with single language code."""
        input_file = "/path/to/movie.en.ass"
        expected = "/path/to/movie.en.mono.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_fallback_with_three_language_codes(self):
        """Test fallback with three language codes."""
        input_file = "/path/to/movie.en-zh-fr.ass"
        expected = "/path/to/movie.en-zh-fr.mono.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_complex_filename(self):
        """Test with complex filename containing special characters."""
        input_file = "/path/to/Movie Name (2023) - S01E01.en-fr.ass"
        expected = "/path/to/Movie Name (2023) - S01E01.fr.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_no_extension(self):
        """Test with filename without extension."""
        input_file = "/path/to/movie.en-zh"
        expected = "/path/to/movie.zh.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected

    def test_multiple_dots_in_path(self):
        """Test with multiple dots in the path."""
        input_file = "/path/to/my.movie.v2.en-de.ass"
        expected = "/path/to/my.movie.v2.de.ass"
        result = generate_mono_output_filename(input_file)
        assert result == expected
