#!/usr/bin/env python3
"""
Validation subcommand for AI Subtitle Translator.

This module provides validation functionality for existing translated ASS files,
allowing users to check translation quality and detect sync issues after translation.
"""

import csv
import os

import pysubs2

from .console_utils import (
    console,
    print_error_with_help,
    print_info,
    print_processing,
    print_warning,
)
from .translation_validator import (
    ValidationResult,
    detect_translation_sync_issues,
    get_validation_summary,
)


def parse_bilingual_ass_file(file_path: str) -> list[tuple[int, str, str]]:
    """
    Parse a bilingual ASS file and extract original and translated text pairs.

    Args:
        file_path: Path to the bilingual ASS file

    Returns:
        List of (index, original_text, translated_text) tuples

    Raises:
        ValueError: If file format is invalid or not bilingual
    """
    try:
        subs = pysubs2.load(file_path)
    except Exception as e:
        raise ValueError(f"Failed to load ASS file: {e}") from e

    pairs = []

    for i, line in enumerate(subs):
        # Use plaintext to get clean text without ASS formatting
        text = line.plaintext.strip()

        # Skip empty lines
        if not text:
            continue

        # Split bilingual text (assumes format: "Original\nTranslation" after plaintext conversion)
        if "\n" in text:
            parts = text.split("\n", 1)
            if len(parts) == 2:
                original = parts[0].strip()
                translated = parts[1].strip()

                if original and translated:
                    pairs.append((i, original, translated))
        else:
            # Monolingual - skip for validation (can't compare ratios)
            continue

    if not pairs:
        raise ValueError(
            "No bilingual subtitle pairs found. File may be monolingual or have invalid format."
        )

    return pairs


def validate_ass_file(
    file_path: str,
    outlier_threshold: float = 0.30,
    extreme_threshold: float = 0.15,
    batch_size: int = 50,
    batch_range: str = None,
) -> list[ValidationResult]:
    """
    Validate translation quality in an ASS file by analyzing batches.

    Args:
        file_path: Path to the ASS file to validate
        outlier_threshold: Outlier percentage threshold for sync issue detection
        extreme_threshold: Extreme ratio percentage threshold
        batch_size: Number of subtitle pairs per validation batch
        batch_range: Optional range like "1-50" to validate specific batches

    Returns:
        List of ValidationResult objects for each batch
    """
    print_processing(f"Parsing bilingual ASS file: {file_path}")

    try:
        pairs = parse_bilingual_ass_file(file_path)
    except ValueError as e:
        print_error_with_help(
            str(e), "Make sure the file is a valid bilingual ASS file."
        )
        return []

    print_info(f"Found {len(pairs)} bilingual subtitle pairs")

    # Split into batches
    batches = []
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i : i + batch_size]
        batches.append((i // batch_size + 1, batch))

    # Filter batches by range if specified
    if batch_range:
        try:
            start_batch, end_batch = map(int, batch_range.split("-"))
            batches = [
                (batch_num, batch)
                for batch_num, batch in batches
                if start_batch <= batch_num <= end_batch
            ]
            print_info(
                f"Validating batches {start_batch}-{end_batch} ({len(batches)} batches)"
            )
        except ValueError:
            print_warning(
                f"Invalid batch range format: {batch_range}. Validating all batches."
            )

    results = []

    for batch_num, batch in batches:
        print_processing(
            f"Validating batch {batch_num}/{len(batches)} ({len(batch)} pairs)"
        )

        # Convert to format expected by validator
        original_batch = [(idx, original) for idx, original, _ in batch]
        translations = {idx: translated for idx, _, translated in batch}

        result = detect_translation_sync_issues(
            original_batch,
            translations,
            outlier_threshold=outlier_threshold,
            extreme_ratio_threshold=extreme_threshold,
        )

        result.batch_number = batch_num  # Add batch number for reporting
        results.append(result)

        # Print batch summary
        summary = get_validation_summary(result)
        if result.is_valid:
            print_info(f"Batch {batch_num}: {summary}")
        else:
            print_warning(f"Batch {batch_num}: ⚠️  {summary}")

    return results


def export_validation_to_csv(results: list[ValidationResult], csv_path: str) -> None:
    """Export validation results to CSV file."""
    print_processing(f"Exporting validation results to: {csv_path}")

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow(
            [
                "batch_number",
                "is_valid",
                "confidence_score",
                "outlier_percentage",
                "extreme_percentage",
                "count",
                "median_ratio",
                "mad",
                "outlier_indices",
            ]
        )

        # Data rows
        for result in results:
            batch_num = getattr(result, "batch_number", 0)
            writer.writerow(
                [
                    batch_num,
                    result.is_valid,
                    f"{result.confidence_score:.3f}",
                    f"{result.outlier_percentage:.3f}",
                    f"{result.stats.get('extreme_percentage', 0):.3f}",
                    result.stats.get("count", 0),
                    f"{result.stats.get('median', 0):.3f}",
                    f"{result.stats.get('mad', 0):.3f}",
                    (
                        ";".join(map(str, result.outlier_indices))
                        if result.outlier_indices
                        else ""
                    ),
                ]
            )

    print_info(f"Validation results exported to: {csv_path}")


def validate_subcommand(args) -> int:
    """Execute the validate subcommand."""
    if not os.path.isfile(args.input_file):
        print_error_with_help(
            f"Input file '{args.input_file}' not found.",
            "Please check the file path and try again.",
        )
        return 1

    if not args.input_file.lower().endswith(".ass"):
        print_error_with_help(
            "Validation requires an ASS file (*.ass).",
            "Please provide a bilingual ASS subtitle file.",
        )
        return 1

    print_info(f"Validating translation quality: {args.input_file}")

    # Run validation
    results = validate_ass_file(
        args.input_file,
        outlier_threshold=args.outlier_threshold,
        extreme_threshold=args.extreme_threshold,
        batch_range=args.batch_range,
    )

    if not results:
        return 1

    # Print overall summary
    valid_batches = sum(1 for r in results if r.is_valid)
    total_batches = len(results)

    console.print("\n" + "=" * 60)
    console.print("[bold]Validation Summary[/bold]")
    console.print(f"Valid batches: {valid_batches}/{total_batches}")
    console.print(f"Success rate: {valid_batches/total_batches:.1%}")

    if args.detailed:
        console.print("\n[bold]Detailed Statistics:[/bold]")
        for result in results:
            batch_num = getattr(result, "batch_number", 0)
            stats = result.stats
            console.print(f"Batch {batch_num}:")
            console.print(f"  - Count: {stats.get('count', 0)}")
            console.print(f"  - Median ratio: {stats.get('median', 0):.3f}")
            console.print(f"  - MAD: {stats.get('mad', 0):.3f}")
            console.print(f"  - Outlier %: {result.outlier_percentage:.1%}")
            console.print(f"  - Extreme %: {stats.get('extreme_percentage', 0):.1%}")
            console.print(f"  - Confidence: {result.confidence_score:.1%}")
            if result.outlier_indices:
                console.print(f"  - Outlier indices: {result.outlier_indices}")

    # Export to CSV if requested
    if args.export_csv:
        export_validation_to_csv(results, args.export_csv)

    console.print("=" * 60)

    # Print recommendations
    if valid_batches < total_batches:
        failed_batches = total_batches - valid_batches
        print_warning(f"{failed_batches} batch(es) show potential sync issues")
        print_info(
            "Consider re-translating problematic sections or adjusting batch size"
        )
    else:
        print_info("All batches passed validation! Translation quality looks good.")

    return 0
