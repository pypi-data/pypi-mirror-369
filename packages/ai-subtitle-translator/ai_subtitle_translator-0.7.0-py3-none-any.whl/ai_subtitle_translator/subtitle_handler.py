"""
Subtitle handling functionality for the subtitle translation system.
"""

import re

import pysubs2

from . import config
from .utils import format_timestamp


def int_to_ass_color(color_int):
    """Convert integer color to ASS color format."""
    return f"&H{color_int:06X}"


class SubtitleHandler:
    """
    Handles subtitle file operations including loading, styling, and saving.
    """

    def __init__(self):
        # Compile the regex pattern for cleaning subtitle text
        self.tag_regex = re.compile(config.SRT_TAG_PATTERN)

    def load_subtitles(self, input_file):
        """
        Load subtitle file with automatic encoding detection.

        Args:
            input_file: Path to the subtitle file

        Returns:
            pysubs2.SSAFile: Subtitle object
        """
        # Try to load the subtitle file with different encodings
        encodings = ["utf-8", "utf-16", "cp1252"]
        subs = None

        for encoding in encodings:
            try:
                subs = pysubs2.load(input_file, encoding=encoding)
                print(f"Successfully read file using {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue

        if subs is None:
            raise ValueError(
                f"Failed to decode file with any of the attempted encodings: {encodings}"
            )

        return subs

    def setup_styles(self, subs):
        """
        Set up styles and info for the subtitle object.

        Args:
            subs: Subtitle object

        Returns:
            str: The formatted separator for Chinese text
        """
        # Set PlayResX and PlayResY
        subs.info["PlayResX"] = config.PLAY_RES_X
        subs.info["PlayResY"] = config.PLAY_RES_Y

        # Add Source style for original language text
        subs.styles[config.SOURCE_STYLE] = pysubs2.SSAStyle(
            fontname=config.TOP_TEXT_FONTNAME,
            fontsize=config.TOP_TEXT_FONTSIZE,
            primarycolor=config.TOP_TEXT_COLOR,
            secondarycolor=config.TOP_TEXT_SECONDARY_COLOR,
            outlinecolor=config.TOP_TEXT_OUTLINE_COLOR,
            backcolor=config.TOP_TEXT_BACK_COLOR,
            bold=False,
            italic=False,
            underline=False,
            strikeout=False,
            scalex=100,
            scaley=100,
            spacing=0,
            angle=0,
            borderstyle=1,
            outline=2,
            shadow=1,
            alignment=pysubs2.common.Alignment.BOTTOM_CENTER,
            marginl=5,
            marginr=5,
            marginv=2,
        )

        # Prepare the separator with translated text formatting
        bottom_color_str = int_to_ass_color(config.BOTTOM_TEXT_COLOR)
        bottom_tag = (
            f"\\fn{config.BOTTOM_TEXT_FONTNAME}"
            f"\\fs{config.BOTTOM_TEXT_FONTSIZE}\\c{bottom_color_str}"
        )
        return f"\\N{{{bottom_tag}}}"

    def setup_monolingual_styles(self, subs):
        """
        Set up styles for monolingual extracted subtitles.

        Creates MonoExtracted style by copying Source and modifying only:
        - fontname: Translated text font (from config)
        - fontsize: Translated text size (from config)
        - primarycolor: Translated text color (from config)
        - marginv: 16 (better positioning for monolingual)

        Args:
            subs: Subtitle object
        """
        # Set up basic info and create Source style first
        self.setup_styles(subs)

        # Copy Source style and modify only what's needed
        mono_style = subs.styles[config.SOURCE_STYLE].copy()
        mono_style.fontname = config.BOTTOM_TEXT_FONTNAME  # Translated text font
        mono_style.fontsize = config.BOTTOM_TEXT_FONTSIZE  # Translated text size
        mono_style.primarycolor = config.BOTTOM_TEXT_COLOR  # Translated text color
        mono_style.marginv = 16  # Better positioning for monolingual

        subs.styles["MonoExtracted"] = mono_style

    def prepare_lines_for_translation(self, subs):
        """
        Prepare subtitle lines for translation.

        Args:
            subs: Subtitle object

        Returns:
            tuple: (lines_to_translate, total_lines)
            lines_to_translate contains tuples: (index, cleaned_text, start, end)
        """
        total_lines = 0
        lines_to_translate = []

        for i, line in enumerate(subs):
            if line.type == "Dialogue":
                line.style = config.SOURCE_STYLE
                total_lines += 1

                # Clean the text: remove tags and replace \N with space
                cleaned_text = self.tag_regex.sub("", line.text)
                cleaned_text = cleaned_text.replace("\\N", " ").strip()

                # Store line index, cleaned text, start time, and end time
                lines_to_translate.append((i, cleaned_text, line.start, line.end))

        return lines_to_translate, total_lines

    def apply_translations(self, subs, translations, separator):
        """
        Apply translations to subtitle lines.

        Args:
            subs: Subtitle object
            translations: Dictionary of translations
            separator: Formatted separator for Chinese text
        """
        for i, line in enumerate(subs):
            if i in translations and translations[i]:
                # Add the translated text as bottom text
                line.text = f"{line.text}{separator}{translations[i]}"

    def apply_translations_replace(self, subs, translations):
        """
        Apply translations by replacing the original text.

        Args:
            subs: Subtitle object
            translations: Dictionary of translations
        """
        for i, line in enumerate(subs):
            if i in translations and translations[i]:
                # Replace the original text with the translated text
                line.text = translations[i]

    def save_subtitles(self, subs, output_file):
        """
        Save the subtitle file as ASS.

        Args:
            subs: Subtitle object
            output_file: Path to the output file
        """
        subs.save(output_file, encoding="utf-8")
        print(f"Saved subtitle file to: {output_file}")

    def extract_monolingual_from_bilingual(self, input_file, output_file):
        """
        Extract monolingual subtitle file from bilingual ASS file.

        Converts bilingual ASS files (with both original and translated text)
        to monolingual ASS files containing only the translated text with proper styling.

        Args:
            input_file: Path to the bilingual ASS file
            output_file: Path to the output monolingual ASS file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load the bilingual ASS file
            subs = self.load_subtitles(input_file)

            # Pattern to match bilingual format: "Original\N{\fnFont\fs36\c&Hcolor&}Translated"
            bilingual_pattern = re.compile(r".*?\\N\{\\fn[^}]*\}(.+)$")

            extracted_count = 0
            total_lines = 0

            for line in subs:
                if line.type == "Dialogue":
                    total_lines += 1

                    # Try to extract translated text from bilingual format
                    match = bilingual_pattern.match(line.text)
                    if match:
                        # Extract the translated text (after the formatting tags)
                        translated_text = match.group(1).strip()

                        # Replace the line text with just the translated text
                        line.text = translated_text

                        # Apply proper monolingual styling
                        line.style = "MonoExtracted"

                        extracted_count += 1
                    else:
                        # If no bilingual pattern found, keep original text but apply monolingual styling
                        line.style = "MonoExtracted"

            # Setup styles for the output file with proper monolingual style
            self.setup_monolingual_styles(subs)

            # Save the monolingual ASS file
            subs.save(output_file, encoding="utf-8")

            print(f"Extracted {extracted_count}/{total_lines} translated lines")
            print(f"Saved monolingual subtitle file to: {output_file}")

            return True

        except Exception as e:
            print(f"Error extracting monolingual subtitles: {e}")
            return False

    def create_timestamp_mapping(self, batch):
        """
        Create a mapping from timestamp to line index for a batch of subtitle lines.

        Args:
            batch: List of subtitle line tuples

        Returns:
            dict: Mapping from timestamp string to line index
        """
        timestamp_to_idx = {}
        for idx, _, start_ms, end_ms in batch:
            timestamp = f"{format_timestamp(start_ms)}-->{format_timestamp(end_ms)}"
            timestamp_to_idx[timestamp] = idx
        return timestamp_to_idx
