"""Tests for adaptive batching functionality."""

import pytest

from ai_subtitle_translator.translate_subtitles import (
    create_adaptive_batch,
    ends_with_sentence_punctuation,
)


class TestSentenceDetection:
    """Test cases for sentence ending detection."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            # Basic punctuation
            ("Hello world.", True),
            ("How are you?", True),
            ("Great!", True),
            # Multiple punctuation
            ("Wait...", True),
            ("Really?!", True),
            ("What!?", True),
            # Quotes after punctuation
            ('He said "Hello."', True),
            ("She said 'Yes!'", True),
            ('The book "War and Peace."', True),
            # Smart quotes (skip for now - can be added later if needed)
            # ("He said \u201cHello.\u201d", True),
            # ("She said \u2018Yes!\u2019", True),
            # Parentheses after punctuation
            ("End of story.)", True),
            ("Are you sure?)", True),
            # Incomplete sentences
            ("Incomplete sentence", False),
            ("No punctuation here", False),
            ("Mr. Smith", False),  # Abbreviation
            ("Dr. Jones", False),
            # Empty/whitespace
            ("", False),
            ("   ", False),
            ("\\n\\t  ", False),
        ],
    )
    def test_ends_with_sentence_punctuation(self, text, expected):
        """Test sentence ending detection with various inputs."""
        result = ends_with_sentence_punctuation(text)
        assert result == expected, f"Failed for text: '{text}'"


class TestAdaptiveBatching:
    """Test cases for adaptive batch creation."""

    @pytest.fixture
    def mock_subtitle_lines(self):
        """Create mock subtitle lines for testing."""
        return [
            (0, "Once upon a time", 0, 1000),
            (1, "there was a story", 1000, 2000),
            (2, "about a brave knight.", 2000, 3000),  # Ends with period
            (3, "He traveled far", 3000, 4000),
            (4, "and wide looking", 4000, 5000),
            (5, "for adventure!", 5000, 6000),  # Ends with exclamation
            (6, "The end", 6000, 7000),
            (7, "of his journey.", 7000, 8000),  # Ends with period
            (8, "What happened next?", 8000, 9000),  # Ends with question
            (9, "Nobody knows", 9000, 10000),
        ]

    def test_batch_ends_with_sentence_completion(self, mock_subtitle_lines):
        """Test batch that naturally ends with sentence completion."""
        batch, next_index = create_adaptive_batch(
            mock_subtitle_lines, start_index=0, base_batch_size=3
        )

        # Should stop at line 2 which ends with "."
        assert len(batch) == 3
        assert next_index == 3
        assert batch[-1][1] == "about a brave knight."  # Last line ends with period

    def test_batch_needs_extension_to_complete_sentence(self, mock_subtitle_lines):
        """Test batch that needs extension to complete sentence."""
        batch, next_index = create_adaptive_batch(
            mock_subtitle_lines, start_index=3, base_batch_size=2
        )

        # Should extend from 2 to 3 lines to reach line 5 with "!"
        assert len(batch) == 3
        assert next_index == 6
        assert batch[-1][1] == "for adventure!"  # Last line ends with exclamation

    def test_batch_reaches_max_extension(self, mock_subtitle_lines):
        """Test batch that hits maximum extension limit."""
        # Create lines where no sentence ends for a long time
        long_lines = [
            (i, f"Line {i} without ending", i * 1000, (i + 1) * 1000) for i in range(25)
        ]
        # Add a sentence ending at the end
        long_lines.append((25, "Finally ends.", 25000, 26000))

        batch, next_index = create_adaptive_batch(
            long_lines, start_index=0, base_batch_size=3, max_extension=5
        )

        # Should stop at max extension (3 + 5 = 8 lines)
        assert len(batch) == 8
        assert next_index == 8

    def test_last_batch_with_remaining_lines(self, mock_subtitle_lines):
        """Test handling of last batch with remaining lines."""
        batch, next_index = create_adaptive_batch(
            mock_subtitle_lines, start_index=8, base_batch_size=5
        )

        # Only 2 lines remaining (index 8 and 9)
        assert len(batch) == 2
        assert next_index == 10  # Beyond the end
        assert batch[0][1] == "What happened next?"
        assert batch[1][1] == "Nobody knows"

    def test_empty_lines_input(self, mock_subtitle_lines):
        """Test handling of empty input or out-of-bounds start."""
        # Empty lines
        batch, next_index = create_adaptive_batch([], 0, 5)
        assert batch == []
        assert next_index == 0

        # Start index beyond lines
        batch, next_index = create_adaptive_batch(mock_subtitle_lines, 20, 5)
        assert batch == []
        assert next_index == 20

    def test_single_line_batches(self, mock_subtitle_lines):
        """Test batch size of 1 with extension."""
        batch, next_index = create_adaptive_batch(
            mock_subtitle_lines, start_index=0, base_batch_size=1
        )

        # Should extend from 1 line to 3 lines to reach sentence ending
        assert len(batch) == 3
        assert next_index == 3
        assert batch[-1][1] == "about a brave knight."

    def test_batch_already_ends_with_sentence(self, mock_subtitle_lines):
        """Test batch where base size already ends with sentence."""
        batch, next_index = create_adaptive_batch(
            mock_subtitle_lines, start_index=2, base_batch_size=1
        )

        # Should not extend since line 2 already ends with "."
        assert len(batch) == 1
        assert next_index == 3
        assert batch[0][1] == "about a brave knight."

    def test_quoted_sentence_endings(self):
        """Test sentences ending with quotes."""
        lines_with_quotes = [
            (0, "He said", 0, 1000),
            (1, '"Hello there."', 1000, 2000),  # Ends with quote after period
            (2, "She replied", 2000, 3000),
            (3, "'How are you?'", 3000, 4000),  # Ends with quote after question
        ]

        batch, next_index = create_adaptive_batch(
            lines_with_quotes, start_index=0, base_batch_size=1
        )

        # Should extend to include the quoted sentence
        assert len(batch) == 2
        assert next_index == 2
        assert batch[-1][1] == '"Hello there."'
