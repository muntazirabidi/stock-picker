"""Scoring system for equity research."""

from .composite import (
    CompanyScore,
    ScoringWeights,
    UniverseScorer,
    calculate_composite_score,
    print_score_distribution,
    print_top_scores,
)
from .percentile import (
    GROWTH_STAGE_METRICS,
    TRADITIONAL_METRICS,
    MetricConfig,
    calculate_all_percentiles,
    calculate_percentile_rank,
    get_percentile_dataframe,
    winsorize,
)

__all__ = [
    # Composite scoring
    "CompanyScore",
    "ScoringWeights",
    "UniverseScorer",
    "calculate_composite_score",
    "print_top_scores",
    "print_score_distribution",
    # Percentile ranking
    "MetricConfig",
    "calculate_percentile_rank",
    "calculate_all_percentiles",
    "get_percentile_dataframe",
    "winsorize",
    "TRADITIONAL_METRICS",
    "GROWTH_STAGE_METRICS",
]
