#!/usr/bin/env python3
"""
Advanced Subtitle Translator (SRT to ASS)

This script translates SRT subtitle files into styled ASS format with options for
bilingual or monolingual output and different translation granularities.

Features:
- Converts SRT to ASS with rich styling.
- **Bilingual Mode**: Displays original text on top and translated text below.
- **Monolingual Mode**: Replaces original text with the translation.
- **Full Text Prompt**: Translates every line.
- **Selective Difficulty Prompt**: Translates only complex phrases, slang, or cultural references.
- **Resumable**: Automatically saves progress and can resume if interrupted.
- **Batch Processing**: Processes subtitles in batches for efficient and reliable API usage.
- Supports multiple AI providers (OpenAI, Gemini, DeepSeek).

Usage:
    python translate_subtitles.py input.srt --translation-mode bilingual --prompt-template selective_difficulty

Note: Requires an API key for the chosen provider (e.g., OPENAI_API_KEY).
"""

import contextlib
import json
import os

import json_repair

from .ai_translation import translate_batch
from .console_utils import (
    Emojis,
    console,
    create_progress_bar,
    create_summary_panel,
    print_batch_info,
    print_completion_celebration,
    print_config_info,
    print_error,
    print_error_with_help,
    print_file_info,
    print_helpful_tip,
    print_info,
    print_processing,
    print_resume_info,
    print_warning,
    print_welcome_banner,
)
from .subtitle_handler import SubtitleHandler
from .utils import (
    extract_media_info,
    generate_mono_output_filename,
    generate_output_filename,
)


def ends_with_sentence_punctuation(text: str) -> bool:
    """
    Check if text ends with sentence-ending punctuation.

    Args:
        text: The text to check

    Returns:
        bool: True if text ends with sentence-ending punctuation
    """
    if not text or not text.strip():
        return False

    # Remove only trailing whitespace
    text = text.strip()

    # Sentence-ending characters (including quotes and parentheses after punctuation)
    return text.endswith((".", "?", "!", '"', "'", ")", '"', '"', """, """))


def create_adaptive_batch(lines, start_index, base_batch_size, max_extension=20):
    """
    Create an adaptive batch that extends beyond base size to complete sentences.

    Args:
        lines: List of line tuples (index, text, start, end)
        start_index: Starting index in the lines list
        base_batch_size: Base batch size to start with
        max_extension: Maximum additional lines to add beyond base size

    Returns:
        tuple: (batch_lines, next_start_index)
    """
    if start_index >= len(lines):
        return [], start_index

    # Start with base batch size
    end_index = min(start_index + base_batch_size, len(lines))
    batch = lines[start_index:end_index]

    # If we've reached the end of all lines, return what we have
    if end_index >= len(lines):
        return batch, end_index

    # Check if the last line ends with sentence punctuation
    if batch and ends_with_sentence_punctuation(batch[-1][1]):  # [1] is the text
        return batch, end_index

    # Extend the batch until we find a sentence ending or reach max extension
    extension_count = 0
    while (
        end_index < len(lines)
        and extension_count < max_extension
        and not ends_with_sentence_punctuation(lines[end_index - 1][1])
    ):

        batch.append(lines[end_index])
        end_index += 1
        extension_count += 1

    return batch, end_index


def translate_subtitles(
    input_file,
    output_file=None,
    provider="deepseek",
    fallback_provider=None,
    model=None,
    translation_mode="bilingual",
    prompt_template="full_text",
    batch_size=80,
    progress_callback=None,
):
    """
    Translates an SRT subtitle file to a styled ASS file with advanced options.

    Args:
        input_file (str): Path to the input SRT file.
        output_file (str, optional): Path to the output ASS file. Defaults to None.
        provider (str, optional): AI provider ('openai', 'gemini', 'deepseek'). Defaults to "deepseek".
        fallback_provider (str, optional): Fallback AI provider to use if primary fails. Defaults to None.
        model (str, optional): Provider-specific model name. Defaults to None.
        translation_mode (str, optional): 'bilingual' or 'monolingual'. Defaults to "bilingual".
        prompt_template (str, optional): 'selective_difficulty' or 'full_text'.
            Defaults to "selective_difficulty".
        batch_size (int, optional): Number of lines to process per API call. Defaults to 60.
        progress_callback (callable, optional): Callback function for progress updates.
            Should accept (current_batch: int, total_batches: int).

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        media_info = extract_media_info(input_file)
        print_info(f"Detected: {media_info}")

        if not output_file:
            output_file = generate_output_filename(input_file, ".en-zh.ass")

        # Define paths for temporary progress files
        base_name = os.path.splitext(output_file)[0]
        progress_file = f"{base_name}.progress.json"
        translations_file = f"{base_name}.trans.json"

        subtitle_handler = SubtitleHandler()
        subs = subtitle_handler.load_subtitles(input_file)
        separator = subtitle_handler.setup_styles(subs)

        # Load existing progress if available
        translated_indices = set()
        all_translations = {}
        if os.path.exists(progress_file) and os.path.exists(translations_file):
            try:
                translated_indices = set(json_repair.from_file(progress_file))
                all_translations = json_repair.from_file(translations_file)
                print_resume_info(len(translated_indices))
            except OSError as e:
                print_warning(
                    f"Could not load progress files. Starting fresh. Error: {e}"
                )
                translated_indices = set()
                all_translations = {}

        lines_to_translate, total_lines = (
            subtitle_handler.prepare_lines_for_translation(subs)
        )

        # Track fallback usage for summary
        fallback_usage = []

        # Filter out lines that have already been translated
        untranslated_lines = [
            line for line in lines_to_translate if line[0] not in translated_indices
        ]

        if not untranslated_lines:
            print_info(
                "All lines have already been translated. Proceeding to file generation."
            )
        else:
            print_processing(
                f"Translating {len(untranslated_lines)} remaining lines..."
            )
            # Estimate total batches (will be updated as we process)
            estimated_batches = (len(untranslated_lines) + batch_size - 1) // batch_size

            # Only use Rich progress bar in CLI mode, not when API provides callback
            if progress_callback is None:
                progress_context = create_progress_bar()
            else:
                progress_context = contextlib.nullcontext(None)

            with progress_context as progress:
                if progress is not None:
                    batch_task = progress.add_task(
                        f"{Emojis.BATCH} Processing batches...", total=estimated_batches
                    )
                else:
                    batch_task = None

                # Use adaptive batching
                current_index = 0
                current_batch_num = 1
                current_total_batches = estimated_batches

                while current_index < len(untranslated_lines):
                    # Create adaptive batch
                    batch, next_index = create_adaptive_batch(
                        untranslated_lines, current_index, batch_size, max_extension=20
                    )

                    if not batch:
                        break

                    batch_line_indices = [line[0] for line in batch]

                    # Update total batches estimate if we're extending beyond base size
                    if len(batch) > batch_size:
                        # Recalculate remaining estimated batches
                        remaining_lines = len(untranslated_lines) - next_index
                        remaining_batches = max(
                            1, (remaining_lines + batch_size - 1) // batch_size
                        )
                        new_total = current_batch_num + remaining_batches
                        if new_total != current_total_batches:
                            current_total_batches = new_total
                            if progress is not None:
                                progress.update(batch_task, total=new_total)

                    print_batch_info(
                        batch_line_indices[0],
                        batch_line_indices[-1],
                        current_batch_num,
                        current_total_batches,
                    )

                    # Add info about adaptive batch size
                    if len(batch) > batch_size:
                        print_info(
                            f"📝 Extended batch to {len(batch)} lines to complete sentences"
                        )

                    current_index = next_index

                    # Extract text lines and indices for array-based translation
                    batch_indices, batch_texts, _, _ = zip(*batch, strict=False)

                    translation_array, fallback_info = translate_batch(
                        provider=provider,
                        prompt_template=prompt_template,
                        text_lines=batch_texts,
                        media_info=media_info,
                        model=model,
                        fallback_provider=fallback_provider,
                    )

                    # Track fallback usage if it occurred
                    if fallback_info:
                        line_start = (
                            min(batch_indices) + 1
                        )  # Convert to 1-based line numbers
                        line_end = max(batch_indices) + 1
                        fallback_usage.append(
                            {
                                "provider": fallback_info["provider"],
                                "line_start": line_start,
                                "line_end": line_end,
                                "count": fallback_info["count"],
                            }
                        )

                    # Map array results back to indices
                    new_translations = {
                        batch_indices[i]: translation_array[i]
                        for i in range(min(len(batch_indices), len(translation_array)))
                        if i < len(translation_array) and translation_array[i].strip()
                    }

                    # Update progress and save incrementally
                    all_translations.update(new_translations)
                    translated_indices.update(new_translations.keys())

                    with open(progress_file, "w", encoding="utf-8") as f:
                        json.dump(list(translated_indices), f)
                    with open(translations_file, "w", encoding="utf-8") as f:
                        json.dump(all_translations, f)

                    if progress is not None:
                        progress.update(batch_task, advance=1)
                    completed_msg = (
                        f"Completed batch. Total translated: "
                        f"{len(translated_indices)}/{total_lines}"
                    )
                    print_info(completed_msg)

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(current_batch_num, current_total_batches)

                    current_batch_num += 1

        # Apply translations based on the selected mode
        if translation_mode == "bilingual":
            subtitle_handler.apply_translations(subs, all_translations, separator)
        elif translation_mode == "monolingual":
            subtitle_handler.apply_translations_replace(subs, all_translations)

        subtitle_handler.save_subtitles(subs, output_file)

        # Clean up temporary files
        for temp_file in [progress_file, translations_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        # Display summary panel
        summary_panel = create_summary_panel(
            status="Success!",
            output_file=output_file,
            mode=translation_mode,
            template=prompt_template,
            provider=provider,
            translated_count=len(all_translations),
            total_count=total_lines,
            fallback_usage=fallback_usage,
        )
        console.print(summary_panel)

        # Print celebration
        print_completion_celebration(len(all_translations), total_lines)

        return True

    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        print_helpful_tip("Check your API keys and internet connection")
        import traceback

        traceback.print_exc()
        return False


def translate_subcommand(args) -> int:
    print_welcome_banner()

    if not os.path.isfile(args.input_file):
        print_error_with_help(
            f"Input file '{args.input_file}' not found.",
            "Please check the file path and try again.",
        )
        return 1

    # Handle extraction mode
    if args.extract_monolingual:
        if not args.input_file.lower().endswith(".ass"):
            print_error_with_help(
                "Extract mode requires an ASS file (*.ass).",
                "Please provide a bilingual ASS subtitle file.",
            )
            return 1

        # Generate output filename for extraction
        output_file = args.output
        if not output_file:
            output_file = generate_mono_output_filename(args.input_file)

        print_file_info(args.input_file, output_file)
        print_info("Extracting monolingual subtitles from bilingual ASS file...")

        subtitle_handler = SubtitleHandler()
        success = subtitle_handler.extract_monolingual_from_bilingual(
            args.input_file, output_file
        )

        if success:
            print_helpful_tip(f"Monolingual ASS file ready: '{output_file}'")
            return 0
        else:
            return 1

    # Handle translation mode (original functionality)
    if not args.input_file.lower().endswith(".srt"):
        print_error_with_help(
            "Input file must be an SRT file (*.srt).",
            "Please provide a valid SRT subtitle file.",
        )
        return 1

    # Generate output filename if not provided
    output_file = args.output
    if not output_file:
        output_file = generate_output_filename(args.input_file, ".en-zh.ass")

    # Display file and configuration info
    print_file_info(args.input_file, output_file)
    print_config_info(
        args.provider, args.translation_mode, args.prompt_template, args.batch_size
    )

    # Add helpful tip
    print_helpful_tip(
        "Translation may take a few minutes depending on file size and batch size"
    )
    console.print()

    success = translate_subtitles(
        args.input_file,
        output_file,
        args.provider,
        args.fallback_provider,
        args.model,
        args.translation_mode,
        args.prompt_template,
        args.batch_size,
    )

    if success:
        print_helpful_tip(
            f"You can now use the ASS file '{output_file}' with your media player"
        )
        return 0
    else:
        return 1


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Advanced subtitle translator (SRT to ASS).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", help="Input SRT or ASS subtitle file.")
    parser.add_argument(
        "-o", "--output", help="Output ASS file path (default: [input_file].ass)."
    )

    # Extraction mode
    parser.add_argument(
        "--extract-monolingual",
        action="store_true",
        help="Extract monolingual subtitles from bilingual ASS file.\n"
        "Converts bilingual ASS files to monolingual versions with proper styling.",
    )

    # Core translation options
    parser.add_argument(
        "--translation-mode",
        choices=["bilingual", "monolingual"],
        default="bilingual",
        help="bilingual: Appends translation below original text.\n"
        "monolingual: Replaces original text with translation.",
    )
    parser.add_argument(
        "--prompt-template",
        choices=["full_text", "selective_difficulty"],
        default="full_text",
        help="full_text: Translates every line.\n"
        "selective_difficulty: Translates only complex/idiomatic lines.",
    )

    # Provider and model options
    parser.add_argument(
        "-p",
        "--provider",
        choices=["openai", "gemini", "deepseek"],
        default="deepseek",
        help="AI provider for translation (default: deepseek).",
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Specific model to use (provider-specific model name).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=80,
        help="Number of lines to process in each API call (default: 80).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume incomplete translation from saved progress.\n"
        "Useful for large files or after interruption.",
    )

    args = parser.parse_args()

    # Call translate_subcommand for direct script execution
    exit_code = translate_subcommand(args)
    sys.exit(exit_code)
