#!/usr/bin/env python3
"""
Main CLI dispatcher for AI Subtitle Translator.

This module provides the main entry point for the CLI tool, routing commands
to appropriate subcommands (translate, validate, etc.).
"""

import argparse
import sys

from .console_utils import print_error_with_help, print_welcome_banner


def create_main_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="ai-subtitle-translator",
        description="Advanced subtitle translator with LLM support",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND",
    )

    # Translate subcommand
    translate_parser = subparsers.add_parser(
        "translate",
        help="Translate subtitle files (SRT to ASS with AI translation)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add_translate_arguments(translate_parser)

    # Validate subcommand
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate translation quality of existing ASS files",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add_validate_arguments(validate_parser)

    return parser


def add_translate_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the translate subcommand."""
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
        "--fallback-provider",
        choices=["openai", "gemini", "deepseek"],
        help="Fallback provider to use if primary provider fails (optional).",
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

    # Output and progress options
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume incomplete translation from saved progress.\n"
        "Useful for large files or after interruption.",
    )


def add_validate_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the validate subcommand."""
    parser.add_argument("input_file", help="Input ASS subtitle file to validate.")
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed validation analysis with statistics.",
    )
    parser.add_argument(
        "--export-csv",
        metavar="FILE",
        help="Export validation results to CSV file.",
    )
    parser.add_argument(
        "--batch-range",
        metavar="START-END",
        help="Validate specific batch range (e.g., 1-50).",
    )
    parser.add_argument(
        "--outlier-threshold",
        type=float,
        default=0.30,
        help="Outlier percentage threshold for sync issue detection (default: 0.30).",
    )
    parser.add_argument(
        "--extreme-threshold",
        type=float,
        default=0.15,
        help="Extreme ratio percentage threshold (default: 0.15).",
    )


def handle_legacy_usage(args: list[str]) -> list[str]:
    """Handle legacy usage patterns for backward compatibility."""
    if not args:
        return args

    # If first argument is not a known subcommand and ends with .srt/.ass,
    # assume it's a file and prepend 'translate'
    known_commands = {"translate", "validate", "--help", "-h"}
    first_arg = args[0]

    if first_arg not in known_commands and (
        first_arg.endswith((".srt", ".ass")) or first_arg.startswith("-")
    ):
        return ["translate"] + args

    return args


def main() -> None:
    """Main entry point for the CLI."""
    # Handle legacy usage patterns
    args = handle_legacy_usage(sys.argv[1:])

    parser = create_main_parser()
    parsed_args = parser.parse_args(args)

    # If no command specified, show help
    if not parsed_args.command:
        print_welcome_banner()
        parser.print_help()
        return

    # Route to appropriate subcommand
    exit_code = 0
    if parsed_args.command == "translate":
        from .translate_subtitles import translate_subcommand

        exit_code = translate_subcommand(parsed_args)
    elif parsed_args.command == "validate":
        from .validate_subtitles import validate_subcommand

        exit_code = validate_subcommand(parsed_args) or 0
    else:
        print_error_with_help(
            f"Unknown command: {parsed_args.command}",
            "Use --help to see available commands.",
        )
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
