"""Tests for CLI functionality."""

import subprocess
import sys
from pathlib import Path


class TestCLI:
    """Test cases for CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                "--help",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "Advanced subtitle translator" in result.stdout
        assert "translate" in result.stdout
        assert "validate" in result.stdout

    def test_cli_extract_flag_present(self):
        """Test that extract-monolingual flag is available in translate subcommand."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                "translate",
                "--help",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        help_text = result.stdout
        assert "--extract-monolingual" in help_text
        assert "bilingual ASS file" in help_text

    def test_cli_extraction_missing_file(self):
        """Test CLI extraction with missing input file."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                "nonexistent.ass",
                "--extract-monolingual",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_cli_extraction_wrong_file_type(self, sample_srt_file):
        """Test CLI extraction with wrong file type (SRT instead of ASS)."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                str(sample_srt_file),
                "--extract-monolingual",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 1
        assert "ASS file" in result.stderr

    def test_cli_extraction_success(self, sample_bilingual_ass_file, temp_dir):
        """Test successful CLI extraction."""
        output_file = temp_dir / "cli_test_output.ass"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                str(sample_bilingual_ass_file),
                "--extract-monolingual",
                "-o",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert output_file.exists()
        assert "Extracted" in result.stdout
        assert "Monolingual ASS file ready" in result.stdout

    def test_cli_extraction_default_output_name(self, sample_bilingual_ass_file):
        """Test CLI extraction with default output filename generation."""
        # The default output should be input_file.mono.ass
        expected_output = sample_bilingual_ass_file.parent / (
            sample_bilingual_ass_file.stem + ".mono.ass"
        )

        # Clean up any existing output file
        if expected_output.exists():
            expected_output.unlink()

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                str(sample_bilingual_ass_file),
                "--extract-monolingual",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        try:
            assert result.returncode == 0
            assert expected_output.exists()
        finally:
            # Clean up
            if expected_output.exists():
                expected_output.unlink()

    def test_cli_extraction_en_zh_naming(self, sample_en_zh_ass_file):
        """Test CLI extraction with .en-zh.ass naming generates .zh.ass output."""
        # The default output should be movie.zh.ass for movie.en-zh.ass input
        expected_output = sample_en_zh_ass_file.parent / "movie.zh.ass"

        # Clean up any existing output file
        if expected_output.exists():
            expected_output.unlink()

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                str(sample_en_zh_ass_file),
                "--extract-monolingual",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        try:
            assert result.returncode == 0
            assert expected_output.exists()
            assert "Extracted" in result.stdout
            assert "movie.zh.ass" in result.stdout
        finally:
            # Clean up
            if expected_output.exists():
                expected_output.unlink()

    def test_cli_extraction_language_neutral_naming(self, sample_en_fr_ass_file):
        """Test CLI extraction with .en-fr.ass naming generates .fr.ass output (language-neutral)."""
        # The default output should be movie.fr.ass for movie.en-fr.ass input
        expected_output = sample_en_fr_ass_file.parent / "movie.fr.ass"

        # Clean up any existing output file
        if expected_output.exists():
            expected_output.unlink()

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                str(sample_en_fr_ass_file),
                "--extract-monolingual",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        try:
            assert result.returncode == 0
            assert expected_output.exists()
            assert "Extracted" in result.stdout
            assert "movie.fr.ass" in result.stdout
        finally:
            # Clean up
            if expected_output.exists():
                expected_output.unlink()

    def test_cli_normal_translation_still_works(self, sample_srt_file):
        """Test that normal translation mode still works (should fail without API key)."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_subtitle_translator.main",
                str(sample_srt_file),
                "--translation-mode",
                "bilingual",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env={"DEEPSEEK_API_KEY": ""},  # Ensure no API key
        )

        # Should fail due to missing API key, but CLI parsing should work
        assert "translation" in result.stdout.lower() or "api" in result.stderr.lower()

    def test_cli_input_validation(self):
        """Test CLI input validation for various edge cases."""
        # Test with no arguments
        result = subprocess.run(
            [sys.executable, "-m", "ai_subtitle_translator.translate_subtitles"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 2  # argparse error
        assert "required" in result.stderr or "error" in result.stderr
