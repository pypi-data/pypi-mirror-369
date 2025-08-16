"""Pytest configuration and fixtures for ai-subtitle-translator tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_srt_content():
    """Sample SRT content for testing."""
    return """1
00:00:01,000 --> 00:00:03,000
Hello world, this is a test.

2
00:00:04,000 --> 00:00:06,000
This is the second subtitle line.

3
00:00:07,000 --> 00:00:09,000
And this is the third line."""


@pytest.fixture
def sample_bilingual_ass_content():
    """Sample bilingual ASS content for testing extraction."""
    return """[Script Info]
Title: Test Bilingual
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColor, SecondaryColor, OutlineColor, BackColor, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Source,Arial,46,&HD3D3D3,&HF0000000,&H101010,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,2,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:03.00,Source,,0,0,0,,Hello world\\N{\\fnMicrosoft YaHei\\fs36\\c&H99CCFF&}你好世界
Dialogue: 0,0:00:04.00,0:00:06.00,Source,,0,0,0,,This is a test\\N{\\fnMicrosoft YaHei\\fs36\\c&H99CCFF&}这是一个测试
Dialogue: 0,0:00:07.00,0:00:09.00,Source,,0,0,0,,Third line\\N{\\fnMicrosoft YaHei\\fs36\\c&H99CCFF&}第三行"""


@pytest.fixture
def sample_srt_file(temp_dir, sample_srt_content):
    """Create a temporary SRT file for testing."""
    srt_file = temp_dir / "test.srt"
    srt_file.write_text(sample_srt_content, encoding="utf-8")
    return srt_file


@pytest.fixture
def sample_bilingual_ass_file(temp_dir, sample_bilingual_ass_content):
    """Create a temporary bilingual ASS file for testing."""
    ass_file = temp_dir / "test_bilingual.ass"
    ass_file.write_text(sample_bilingual_ass_content, encoding="utf-8")
    return ass_file


@pytest.fixture
def sample_en_zh_ass_file(temp_dir, sample_bilingual_ass_content):
    """Create a temporary bilingual ASS file with .en-zh.ass naming for testing."""
    ass_file = temp_dir / "movie.en-zh.ass"
    ass_file.write_text(sample_bilingual_ass_content, encoding="utf-8")
    return ass_file


@pytest.fixture
def sample_en_fr_ass_file(temp_dir, sample_bilingual_ass_content):
    """Create a temporary bilingual ASS file with .en-fr.ass naming for testing."""
    ass_file = temp_dir / "movie.en-fr.ass"
    ass_file.write_text(sample_bilingual_ass_content, encoding="utf-8")
    return ass_file
