"""Tests for subtitle_handler module."""

import pysubs2
import pytest

from ai_subtitle_translator import config
from ai_subtitle_translator.subtitle_handler import SubtitleHandler


class TestSubtitleHandler:
    """Test cases for SubtitleHandler class."""

    def test_init(self):
        """Test SubtitleHandler initialization."""
        handler = SubtitleHandler()
        assert handler.tag_regex is not None

    def test_load_subtitles_srt(self, sample_srt_file):
        """Test loading SRT subtitle files."""
        handler = SubtitleHandler()
        subs = handler.load_subtitles(str(sample_srt_file))

        assert isinstance(subs, pysubs2.SSAFile)
        assert len(subs) == 3
        assert subs[0].text == "Hello world, this is a test."
        assert subs[1].text == "This is the second subtitle line."

    def test_load_subtitles_encoding_fallback(self, temp_dir):
        """Test subtitle loading with encoding fallback."""
        # Create a file with specific encoding
        test_file = temp_dir / "test_encoding.srt"
        content = "1\n00:00:01,000 --> 00:00:03,000\nTest content\n"
        test_file.write_text(content, encoding="utf-8")

        handler = SubtitleHandler()
        subs = handler.load_subtitles(str(test_file))

        assert len(subs) == 1
        assert subs[0].text == "Test content"

    def test_load_subtitles_file_not_found(self):
        """Test loading non-existent subtitle file."""
        handler = SubtitleHandler()

        with pytest.raises(FileNotFoundError):
            handler.load_subtitles("nonexistent.srt")

    def test_setup_styles(self):
        """Test style setup for bilingual subtitles."""
        handler = SubtitleHandler()
        subs = pysubs2.SSAFile()

        separator = handler.setup_styles(subs)

        # Check basic info is set
        assert subs.info["PlayResX"] == config.PLAY_RES_X
        assert subs.info["PlayResY"] == config.PLAY_RES_Y

        # Check Source style is created
        assert config.SOURCE_STYLE in subs.styles
        source_style = subs.styles[config.SOURCE_STYLE]
        assert source_style.fontname == config.TOP_TEXT_FONTNAME
        assert source_style.fontsize == config.TOP_TEXT_FONTSIZE
        assert source_style.primarycolor == config.TOP_TEXT_COLOR
        assert source_style.marginv == 2

        # Check separator format
        assert "\\N{" in separator
        assert config.BOTTOM_TEXT_FONTNAME in separator
        assert str(config.BOTTOM_TEXT_FONTSIZE) in separator

    def test_setup_monolingual_styles(self):
        """Test monolingual style setup."""
        handler = SubtitleHandler()
        subs = pysubs2.SSAFile()

        handler.setup_monolingual_styles(subs)

        # Check both styles exist
        assert config.SOURCE_STYLE in subs.styles
        assert "MonoExtracted" in subs.styles

        # Check MonoExtracted style properties
        mono_style = subs.styles["MonoExtracted"]
        assert mono_style.fontname == config.BOTTOM_TEXT_FONTNAME
        assert mono_style.fontsize == config.BOTTOM_TEXT_FONTSIZE
        assert mono_style.primarycolor == config.BOTTOM_TEXT_COLOR
        assert mono_style.marginv == 16  # Better positioning

    def test_prepare_lines_for_translation(self, sample_srt_file):
        """Test preparation of lines for translation."""
        handler = SubtitleHandler()
        subs = handler.load_subtitles(str(sample_srt_file))

        lines_to_translate, total_lines = handler.prepare_lines_for_translation(subs)

        assert total_lines == 3
        assert len(lines_to_translate) == 3

        # Check first line structure
        line_idx, cleaned_text, start, end = lines_to_translate[0]
        assert line_idx == 0
        assert cleaned_text == "Hello world, this is a test."
        assert start == 1000  # 1 second
        assert end == 3000  # 3 seconds

    def test_extract_monolingual_from_bilingual(
        self, sample_bilingual_ass_file, temp_dir
    ):
        """Test extraction of monolingual subtitles from bilingual ASS."""
        handler = SubtitleHandler()
        output_file = temp_dir / "output_mono.ass"

        # Test extraction
        success = handler.extract_monolingual_from_bilingual(
            str(sample_bilingual_ass_file), str(output_file)
        )

        assert success is True
        assert output_file.exists()

        # Load and verify the extracted file
        result_subs = pysubs2.load(str(output_file))

        # Check extracted content
        assert len(result_subs) == 3
        assert result_subs[0].text == "你好世界"
        assert result_subs[1].text == "这是一个测试"
        assert result_subs[2].text == "第三行"

        # Check all lines use MonoExtracted style
        for line in result_subs:
            if line.type == "Dialogue":
                assert line.style == "MonoExtracted"

        # Check MonoExtracted style properties
        mono_style = result_subs.styles["MonoExtracted"]
        assert mono_style.fontname == config.BOTTOM_TEXT_FONTNAME
        assert mono_style.fontsize == config.BOTTOM_TEXT_FONTSIZE
        assert mono_style.marginv == 16

    def test_extract_monolingual_no_bilingual_content(self, temp_dir):
        """Test extraction with ASS file containing no bilingual content."""
        # Create ASS file with only original text
        ass_content = """[Script Info]
Title: Test Monolingual

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColor, SecondaryColor, OutlineColor, BackColor, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Source,Arial,46,&HD3D3D3,&HF0000000,&H101010,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,2,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:03.00,Source,,0,0,0,,Only original text here"""

        input_file = temp_dir / "mono_input.ass"
        output_file = temp_dir / "mono_output.ass"
        input_file.write_text(ass_content, encoding="utf-8")

        handler = SubtitleHandler()
        success = handler.extract_monolingual_from_bilingual(
            str(input_file), str(output_file)
        )

        assert success is True

        # Load result and check it still uses MonoExtracted style
        result_subs = pysubs2.load(str(output_file))
        assert len(result_subs) == 1
        assert result_subs[0].text == "Only original text here"
        assert result_subs[0].style == "MonoExtracted"

    def test_extract_monolingual_file_error(self):
        """Test extraction with invalid input file."""
        handler = SubtitleHandler()

        success = handler.extract_monolingual_from_bilingual(
            "nonexistent.ass", "output.ass"
        )

        assert success is False

    def test_save_subtitles(self, temp_dir):
        """Test saving subtitle files."""
        handler = SubtitleHandler()
        subs = pysubs2.SSAFile()

        # Add a test line
        subs.append(pysubs2.SSAEvent(start=1000, end=3000, text="Test subtitle"))

        output_file = temp_dir / "test_output.ass"
        handler.save_subtitles(subs, str(output_file))

        assert output_file.exists()

        # Verify file can be loaded back
        loaded_subs = pysubs2.load(str(output_file))
        assert len(loaded_subs) == 1
        assert loaded_subs[0].text == "Test subtitle"
