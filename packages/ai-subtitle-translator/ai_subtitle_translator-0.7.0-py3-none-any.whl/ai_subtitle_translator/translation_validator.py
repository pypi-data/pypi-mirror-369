#!/usr/bin/env python3
"""
Translation validation module for detecting sync issues in AI-generated subtitle translations.

This module implements adaptive statistical analysis to detect when LLM translations are out of sync
with their original subtitles, which can happen when the AI shifts indices or returns translations
with mismatched ordering.
"""

import statistics
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of translation validation."""

    is_valid: bool
    confidence_score: float  # 0.0 to 1.0
    outlier_percentage: float
    outlier_indices: list[int]
    stats: dict[str, float]


def detect_translation_sync_issues(
    original_batch: list[tuple[int, str]],
    translations: dict[int, str],
    outlier_threshold: float = 0.30,
    extreme_ratio_threshold: float = 0.15,  # % of extreme ratios to trigger alert
    mad_multiplier: float = 3.0,
    min_batch_size: int = 5,
) -> ValidationResult:
    """
    Detect sync issues in translation batch using adaptive statistical analysis.

    Uses Median Absolute Deviation (MAD) for robust outlier detection within each batch,
    avoiding the need for hard-coded ratio ranges that require manual tuning.

    Args:
        original_batch: List of (index, original_text) tuples
        translations: Dictionary mapping indices to translated text
        outlier_threshold: Maximum allowed outlier percentage (0.0-1.0)
        mad_multiplier: MAD multiplier for outlier detection (typically 2-3)
        min_batch_size: Minimum batch size for statistical analysis

    Returns:
        ValidationResult with validation status and diagnostic information
    """
    # Calculate length ratios for available translations
    ratios = []
    valid_pairs = []

    for idx, original_text in original_batch:
        if idx in translations:
            translated_text = translations[idx]
            original_len = len(original_text.strip())
            translated_len = len(translated_text.strip())

            if original_len > 0 and translated_len > 0:
                ratio = translated_len / original_len
                ratios.append(ratio)
                valid_pairs.append((idx, ratio))

    # Skip analysis if insufficient data
    if len(ratios) < min_batch_size:
        return ValidationResult(
            is_valid=True,  # Assume valid for small batches
            confidence_score=0.5,  # Low confidence due to small sample
            outlier_percentage=0.0,
            outlier_indices=[],
            stats={
                "count": len(ratios),
                "median": statistics.median(ratios) if ratios else 0,
                "mad": 0,
                "reason": f"Insufficient data ({len(ratios)} < {min_batch_size})",
            },
        )

    # Robust statistical analysis using MAD
    median_ratio = statistics.median(ratios)
    mad = statistics.median([abs(r - median_ratio) for r in ratios])

    # Detect outliers using MAD-based threshold
    outlier_indices = []
    if mad > 0:  # Avoid division by zero
        threshold = mad_multiplier * mad
        for idx, ratio in valid_pairs:
            if abs(ratio - median_ratio) > threshold:
                outlier_indices.append(idx)

    # Calculate outlier percentage
    outlier_percentage = len(outlier_indices) / len(ratios)

    # Additional check: extreme ratio distribution (key for sync issues)
    extreme_low_count = sum(
        1 for r in ratios if r < 0.2
    )  # Very short Chinese for long English
    extreme_high_count = sum(
        1 for r in ratios if r > 2.0
    )  # Very long Chinese for short English
    extreme_total = extreme_low_count + extreme_high_count
    extreme_percentage = extreme_total / len(ratios)

    # Determine if batch has sync issues using statistical criteria
    sync_issues_detected = (
        outlier_percentage > outlier_threshold
        or extreme_percentage > extreme_ratio_threshold
    )

    # Calculate confidence score based on statistical reliability
    confidence_score = _calculate_confidence_score(
        len(ratios), outlier_percentage, mad, median_ratio, extreme_percentage
    )

    stats = {
        "count": len(ratios),
        "median": median_ratio,
        "mad": mad,
        "outlier_percentage": outlier_percentage,
        "extreme_percentage": extreme_percentage,
        "extreme_low_count": extreme_low_count,
        "extreme_high_count": extreme_high_count,
        "threshold_used": mad_multiplier * mad if mad > 0 else 0,
    }

    return ValidationResult(
        is_valid=not sync_issues_detected,
        confidence_score=confidence_score,
        outlier_percentage=outlier_percentage,
        outlier_indices=outlier_indices,
        stats=stats,
    )


def _calculate_confidence_score(
    sample_size: int,
    outlier_percentage: float,
    mad: float,
    median_ratio: float,
    extreme_percentage: float,
) -> float:
    """Calculate confidence score based on statistical reliability."""
    score = 1.0

    # Penalize high outlier percentage
    if outlier_percentage > 0.3:
        score *= max(0.2, 1.0 - outlier_percentage)

    # Penalize high extreme ratio percentage (key indicator of sync issues)
    if extreme_percentage > 0.15:
        score *= max(0.1, 1.0 - extreme_percentage * 2)

    # Penalize very low MAD (suggests all ratios are identical - suspicious)
    if mad < 0.01:
        score *= 0.7

    # Penalize extreme median ratios (very likely indicates sync issues)
    if median_ratio < 0.1 or median_ratio > 10.0:
        score *= 0.5

    # Bonus for larger sample sizes (more reliable statistics)
    if sample_size >= 20:
        score *= 1.1
    elif sample_size < 10:
        score *= 0.8

    return min(1.0, max(0.1, score))


def get_validation_summary(result: ValidationResult) -> str:
    """Generate a concise validation summary for logging."""
    status = "VALID" if result.is_valid else "SYNC_ISSUE"
    confidence = f"{result.confidence_score:.1%}"
    outliers = f"{result.outlier_percentage:.1%}"
    extreme = f"{result.stats.get('extreme_percentage', 0):.1%}"
    count = result.stats.get("count", 0)
    median = result.stats.get("median", 0)

    summary = f"[{status}] {count} translations, median_ratio={median:.2f}, outliers={outliers}, extreme={extreme}, confidence={confidence}"

    return summary
