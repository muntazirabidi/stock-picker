"""Composite scoring - combines percentile ranks into overall scores.

Creates stage-adjusted composite scores that weight metrics appropriately
based on whether a company is mature, a compounder, or in growth stage.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from src.data.models import CompanyStage
from src.metrics import CompanyMetrics

from .percentile import (
    GROWTH_STAGE_METRICS,
    TRADITIONAL_METRICS,
    calculate_all_percentiles,
)


@dataclass
class ScoringWeights:
    """Weights for composite score calculation."""

    # Traditional metric category weights
    quality_weight: float = 0.30
    growth_weight: float = 0.25
    strength_weight: float = 0.20
    valuation_weight: float = 0.25

    # Growth stage metric category weights
    revenue_quality_weight: float = 0.30
    efficiency_weight: float = 0.25
    cash_weight: float = 0.20
    dilution_weight: float = 0.15
    trends_weight: float = 0.10


# Default weights by stage
STAGE_WEIGHTS: dict[CompanyStage, ScoringWeights] = {
    CompanyStage.MATURE: ScoringWeights(
        quality_weight=0.35,
        growth_weight=0.15,
        strength_weight=0.25,
        valuation_weight=0.25,
    ),
    CompanyStage.COMPOUNDER: ScoringWeights(
        quality_weight=0.25,
        growth_weight=0.30,
        strength_weight=0.15,
        valuation_weight=0.30,
    ),
    CompanyStage.GROWTH: ScoringWeights(
        revenue_quality_weight=0.30,
        efficiency_weight=0.25,
        cash_weight=0.20,
        dilution_weight=0.15,
        trends_weight=0.10,
    ),
    CompanyStage.SPECULATIVE: ScoringWeights(
        quality_weight=0.25,
        growth_weight=0.25,
        strength_weight=0.25,
        valuation_weight=0.25,
    ),
}

# Metric to category mapping for traditional
TRADITIONAL_CATEGORIES = {
    "quality": ["roic", "roe", "gross_margin", "operating_margin", "fcf_margin"],
    "growth": ["revenue_growth_1y", "revenue_growth_3y", "fcf_growth_1y"],
    "strength": ["current_ratio", "debt_to_equity"],
    "valuation": ["pe_ratio", "ev_to_ebitda", "fcf_yield"],
}

# Metric to category mapping for growth stage
GROWTH_STAGE_CATEGORIES = {
    "revenue_quality": ["gross_margin", "revenue_growth_1y"],
    "efficiency": ["rule_of_40", "operating_leverage"],
    "cash": ["fcf_margin_trend"],
    "dilution": ["sbc_pct_revenue", "share_dilution"],
    "trends": ["gross_margin_trend"],
}


@dataclass
class CompanyScore:
    """Scored company with composite and component scores."""

    ticker: str
    name: str | None
    stage: CompanyStage

    # Overall composite score (0-100)
    composite_score: float | None = None

    # Category scores (0-100)
    quality_score: float | None = None
    growth_score: float | None = None
    strength_score: float | None = None
    valuation_score: float | None = None

    # Growth stage category scores
    revenue_quality_score: float | None = None
    efficiency_score: float | None = None
    cash_score: float | None = None
    dilution_score: float | None = None
    trends_score: float | None = None

    # Individual metric percentiles
    metric_percentiles: dict[str, float | None] = field(default_factory=dict)

    # Market data
    market_cap: float | None = None
    current_price: float | None = None

    @property
    def percentile_rank(self) -> str:
        """Get human-readable percentile rank."""
        if self.composite_score is None:
            return "N/A"
        if self.composite_score >= 90:
            return "Top 10%"
        elif self.composite_score >= 75:
            return "Top 25%"
        elif self.composite_score >= 50:
            return "Top 50%"
        elif self.composite_score >= 25:
            return "Bottom 50%"
        else:
            return "Bottom 25%"


def _calculate_category_score(
    percentiles: dict[str, float | None],
    metrics_in_category: list[str],
) -> float | None:
    """Calculate average score for a category of metrics.

    Args:
        percentiles: Dict of metric name to percentile
        metrics_in_category: List of metric names in this category

    Returns:
        Average percentile or None if no valid metrics
    """
    valid_scores = []

    for metric in metrics_in_category:
        pct = percentiles.get(metric)
        if pct is not None:
            valid_scores.append(pct)

    if not valid_scores:
        return None

    return sum(valid_scores) / len(valid_scores)


def calculate_composite_score(
    metrics: CompanyMetrics,
    percentiles: dict[str, float | None],
    weights: ScoringWeights | None = None,
) -> CompanyScore:
    """Calculate composite score for a company.

    Args:
        metrics: CompanyMetrics for the company
        percentiles: Dict of metric name to percentile rank
        weights: Optional custom weights

    Returns:
        CompanyScore with all scores calculated
    """
    stage = metrics.stage.stage

    if weights is None:
        weights = STAGE_WEIGHTS.get(stage, STAGE_WEIGHTS[CompanyStage.SPECULATIVE])

    score = CompanyScore(
        ticker=metrics.ticker,
        name=metrics.name,
        stage=stage,
        metric_percentiles=percentiles.copy(),
        market_cap=metrics.market_cap,
        current_price=metrics.current_price,
    )

    # Calculate category scores based on stage
    if stage in (CompanyStage.MATURE, CompanyStage.COMPOUNDER, CompanyStage.SPECULATIVE):
        # Use traditional metrics
        score.quality_score = _calculate_category_score(
            percentiles, TRADITIONAL_CATEGORIES["quality"]
        )
        score.growth_score = _calculate_category_score(
            percentiles, TRADITIONAL_CATEGORIES["growth"]
        )
        score.strength_score = _calculate_category_score(
            percentiles, TRADITIONAL_CATEGORIES["strength"]
        )
        score.valuation_score = _calculate_category_score(
            percentiles, TRADITIONAL_CATEGORIES["valuation"]
        )

        # Calculate composite from category scores
        category_scores = [
            (score.quality_score, weights.quality_weight),
            (score.growth_score, weights.growth_weight),
            (score.strength_score, weights.strength_weight),
            (score.valuation_score, weights.valuation_weight),
        ]

        valid_weighted = [
            (s * w, w) for s, w in category_scores if s is not None
        ]

        if valid_weighted:
            total_score = sum(sw[0] for sw in valid_weighted)
            total_weight = sum(sw[1] for sw in valid_weighted)
            score.composite_score = total_score / total_weight

    if stage in (CompanyStage.GROWTH, CompanyStage.COMPOUNDER):
        # Also calculate growth stage metrics
        score.revenue_quality_score = _calculate_category_score(
            percentiles, GROWTH_STAGE_CATEGORIES["revenue_quality"]
        )
        score.efficiency_score = _calculate_category_score(
            percentiles, GROWTH_STAGE_CATEGORIES["efficiency"]
        )
        score.cash_score = _calculate_category_score(
            percentiles, GROWTH_STAGE_CATEGORIES["cash"]
        )
        score.dilution_score = _calculate_category_score(
            percentiles, GROWTH_STAGE_CATEGORIES["dilution"]
        )
        score.trends_score = _calculate_category_score(
            percentiles, GROWTH_STAGE_CATEGORIES["trends"]
        )

        # For pure growth stage, use growth metrics for composite
        if stage == CompanyStage.GROWTH:
            category_scores = [
                (score.revenue_quality_score, weights.revenue_quality_weight),
                (score.efficiency_score, weights.efficiency_weight),
                (score.cash_score, weights.cash_weight),
                (score.dilution_score, weights.dilution_weight),
                (score.trends_score, weights.trends_weight),
            ]

            valid_weighted = [
                (s * w, w) for s, w in category_scores if s is not None
            ]

            if valid_weighted:
                total_score = sum(sw[0] for sw in valid_weighted)
                total_weight = sum(sw[1] for sw in valid_weighted)
                score.composite_score = total_score / total_weight

    return score


class UniverseScorer:
    """Scores an entire universe of stocks."""

    def __init__(self, custom_weights: dict[CompanyStage, ScoringWeights] | None = None):
        """Initialize scorer.

        Args:
            custom_weights: Optional custom weights by stage
        """
        self.weights = custom_weights or STAGE_WEIGHTS

    def score_universe(
        self, metrics_list: Sequence[CompanyMetrics]
    ) -> list[CompanyScore]:
        """Score all companies in the universe.

        Args:
            metrics_list: List of CompanyMetrics for all stocks

        Returns:
            List of CompanyScore, sorted by composite score (descending)
        """
        if not metrics_list:
            return []

        # Calculate percentiles for all metrics
        all_percentiles = calculate_all_percentiles(metrics_list)

        # Calculate composite scores for each company
        scores = []

        for i, metrics in enumerate(metrics_list):
            # Get percentiles for this company
            company_percentiles = {
                metric_name: pct_list[i]
                for metric_name, pct_list in all_percentiles.items()
            }

            # Get appropriate weights
            weights = self.weights.get(
                metrics.stage.stage,
                self.weights[CompanyStage.SPECULATIVE]
            )

            # Calculate score
            score = calculate_composite_score(metrics, company_percentiles, weights)
            scores.append(score)

        # Sort by composite score (descending), None values at end
        scores.sort(
            key=lambda s: (s.composite_score is not None, s.composite_score or 0),
            reverse=True,
        )

        return scores

    def to_dataframe(self, scores: Sequence[CompanyScore]) -> pd.DataFrame:
        """Convert scores to DataFrame.

        Args:
            scores: List of CompanyScore

        Returns:
            DataFrame with all score data
        """
        data: list[dict[str, Any]] = []

        for score in scores:
            row = {
                "ticker": score.ticker,
                "name": score.name,
                "stage": score.stage.value,
                "composite_score": score.composite_score,
                "percentile_rank": score.percentile_rank,
                "quality_score": score.quality_score,
                "growth_score": score.growth_score,
                "strength_score": score.strength_score,
                "valuation_score": score.valuation_score,
                "revenue_quality_score": score.revenue_quality_score,
                "efficiency_score": score.efficiency_score,
                "cash_score": score.cash_score,
                "dilution_score": score.dilution_score,
                "trends_score": score.trends_score,
                "market_cap": score.market_cap,
                "current_price": score.current_price,
            }

            # Add individual metric percentiles
            for metric_name, pct in score.metric_percentiles.items():
                row[f"{metric_name}_pct"] = pct

            data.append(row)

        return pd.DataFrame(data)

    def save_scores(
        self,
        scores: Sequence[CompanyScore],
        path: Path,
        format: str = "parquet",
    ) -> None:
        """Save scores to file.

        Args:
            scores: List of CompanyScore
            path: Output path
            format: "parquet" or "csv"
        """
        df = self.to_dataframe(scores)

        if format == "parquet":
            df.to_parquet(path, index=False)
        else:
            df.to_csv(path, index=False)

    def load_scores(self, path: Path) -> pd.DataFrame:
        """Load scores from file.

        Args:
            path: Path to parquet or csv file

        Returns:
            DataFrame with scores
        """
        if path.suffix == ".parquet":
            return pd.read_parquet(path)
        else:
            return pd.read_csv(path)


def print_top_scores(scores: Sequence[CompanyScore], n: int = 10) -> None:
    """Print top N scoring companies.

    Args:
        scores: List of CompanyScore (should be pre-sorted)
        n: Number to print
    """
    print(f"\n{'='*70}")
    print(f"TOP {n} STOCKS BY COMPOSITE SCORE")
    print(f"{'='*70}")
    print(f"{'Rank':<5} {'Ticker':<8} {'Name':<25} {'Stage':<12} {'Score':>8}")
    print("-" * 70)

    for i, score in enumerate(scores[:n], 1):
        name = (score.name or "")[:24]
        stage = score.stage.value[:11]
        composite = f"{score.composite_score:.1f}" if score.composite_score else "N/A"
        print(f"{i:<5} {score.ticker:<8} {name:<25} {stage:<12} {composite:>8}")

    print("=" * 70)


def print_score_distribution(scores: Sequence[CompanyScore]) -> None:
    """Print distribution of scores.

    Args:
        scores: List of CompanyScore
    """
    valid_scores = [s.composite_score for s in scores if s.composite_score is not None]

    if not valid_scores:
        print("No valid scores to analyze")
        return

    import numpy as np

    print(f"\n{'='*50}")
    print("SCORE DISTRIBUTION")
    print(f"{'='*50}")
    print(f"Total companies: {len(scores)}")
    print(f"Companies with scores: {len(valid_scores)}")
    print(f"\nStatistics:")
    print(f"  Mean: {np.mean(valid_scores):.1f}")
    print(f"  Median: {np.median(valid_scores):.1f}")
    print(f"  Std Dev: {np.std(valid_scores):.1f}")
    print(f"  Min: {np.min(valid_scores):.1f}")
    print(f"  Max: {np.max(valid_scores):.1f}")

    # Distribution by decile
    print(f"\nBy decile:")
    for i in range(10, 0, -1):
        lower = (i - 1) * 10
        upper = i * 10
        count = sum(1 for s in valid_scores if lower <= s < upper)
        bar = "█" * (count // 2)
        print(f"  {lower:2d}-{upper:2d}: {count:3d} {bar}")

    print("=" * 50)
