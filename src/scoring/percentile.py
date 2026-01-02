"""Percentile ranking for metrics across the universe.

Converts raw metric values into percentile ranks (0-100) relative to
the universe of stocks. This normalizes metrics with different scales
and makes them comparable.
"""

from dataclasses import dataclass
from typing import Any, Callable, Sequence

import numpy as np
import pandas as pd

from src.metrics import CompanyMetrics


@dataclass
class MetricConfig:
    """Configuration for a metric's percentile calculation."""

    name: str
    extractor: Callable[[CompanyMetrics], float | None]
    higher_is_better: bool = True
    winsorize_lower: float = 0.01  # Bottom 1%
    winsorize_upper: float = 0.99  # Top 99%


def winsorize(values: np.ndarray, lower: float = 0.01, upper: float = 0.99) -> np.ndarray:
    """Winsorize values to reduce outlier impact.

    Clips values to specified percentiles to prevent extreme outliers
    from distorting the percentile distribution.

    Args:
        values: Array of values
        lower: Lower percentile bound (0-1)
        upper: Upper percentile bound (0-1)

    Returns:
        Winsorized array
    """
    if len(values) == 0:
        return values

    lower_bound = np.nanpercentile(values, lower * 100)
    upper_bound = np.nanpercentile(values, upper * 100)

    return np.clip(values, lower_bound, upper_bound)


def calculate_percentile_rank(
    values: Sequence[float | None],
    higher_is_better: bool = True,
    winsorize_bounds: tuple[float, float] | None = (0.01, 0.99),
) -> list[float | None]:
    """Calculate percentile ranks for a list of values.

    Args:
        values: List of metric values (may contain None)
        higher_is_better: If True, higher values get higher percentiles
        winsorize_bounds: Optional (lower, upper) bounds for winsorization

    Returns:
        List of percentile ranks (0-100) or None for missing values
    """
    # Convert to numpy array, keeping track of valid indices
    arr = np.array([v if v is not None else np.nan for v in values], dtype=float)
    valid_mask = ~np.isnan(arr)

    if valid_mask.sum() == 0:
        return [None] * len(values)

    # Extract valid values
    valid_values = arr[valid_mask]

    # Winsorize if requested
    if winsorize_bounds:
        valid_values = winsorize(valid_values, winsorize_bounds[0], winsorize_bounds[1])
        # Apply back to original array
        arr[valid_mask] = valid_values

    # Calculate percentile ranks using pandas (handles ties properly)
    valid_series = pd.Series(valid_values)

    if higher_is_better:
        ranks = valid_series.rank(method="average", pct=True) * 100
    else:
        # Invert: lower values get higher percentiles
        ranks = (1 - valid_series.rank(method="average", pct=True)) * 100

    # Map back to original indices
    result: list[float | None] = [None] * len(values)
    valid_idx = 0
    for i, is_valid in enumerate(valid_mask):
        if is_valid:
            result[i] = float(ranks.iloc[valid_idx])
            valid_idx += 1

    return result


# Metric extractors for traditional metrics
def extract_roic(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.quality.roic is not None:
        # Cap extreme values
        roic = m.traditional.quality.roic
        if abs(roic) > 1:  # >100% or <-100% is likely data issue
            return None
        return roic
    return None


def extract_roe(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.quality.roe is not None:
        roe = m.traditional.quality.roe
        if abs(roe) > 1:
            return None
        return roe
    return None


def extract_gross_margin(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.quality.gross_margin is not None:
        return m.traditional.quality.gross_margin
    if m.growth_stage and m.growth_stage.revenue_quality.gross_margin is not None:
        return m.growth_stage.revenue_quality.gross_margin
    return None


def extract_operating_margin(m: CompanyMetrics) -> float | None:
    if m.traditional:
        return m.traditional.quality.operating_margin
    return None


def extract_fcf_margin(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.quality.fcf_margin is not None:
        return m.traditional.quality.fcf_margin
    if m.growth_stage and m.growth_stage.cash.fcf_margin is not None:
        return m.growth_stage.cash.fcf_margin
    return None


def extract_revenue_growth_1y(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.growth.revenue_growth_1y is not None:
        return m.traditional.growth.revenue_growth_1y
    if m.growth_stage and m.growth_stage.revenue_quality.revenue_growth_1y is not None:
        return m.growth_stage.revenue_quality.revenue_growth_1y
    return None


def extract_revenue_growth_3y(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.growth.revenue_growth_3y_cagr is not None:
        return m.traditional.growth.revenue_growth_3y_cagr
    if m.growth_stage and m.growth_stage.revenue_quality.revenue_growth_3y_cagr is not None:
        return m.growth_stage.revenue_quality.revenue_growth_3y_cagr
    return None


def extract_fcf_growth_1y(m: CompanyMetrics) -> float | None:
    if m.traditional:
        return m.traditional.growth.fcf_growth_1y
    return None


def extract_current_ratio(m: CompanyMetrics) -> float | None:
    if m.traditional:
        return m.traditional.strength.current_ratio
    return None


def extract_debt_to_equity(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.strength.debt_to_equity is not None:
        de = m.traditional.strength.debt_to_equity
        # Cap extreme values
        if de > 10:  # 1000% debt/equity is extreme
            return 10.0
        return de
    return None


def extract_pe_ratio(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.valuation.pe_ratio is not None:
        pe = m.traditional.valuation.pe_ratio
        if pe <= 0 or pe > 500:  # Negative or extreme PE
            return None
        return pe
    return None


def extract_fcf_yield(m: CompanyMetrics) -> float | None:
    if m.traditional:
        return m.traditional.valuation.fcf_yield
    return None


def extract_ev_to_ebitda(m: CompanyMetrics) -> float | None:
    if m.traditional and m.traditional.valuation.ev_to_ebitda is not None:
        ev = m.traditional.valuation.ev_to_ebitda
        if ev <= 0 or ev > 100:
            return None
        return ev
    return None


# Growth stage metric extractors
def extract_rule_of_40(m: CompanyMetrics) -> float | None:
    if m.growth_stage:
        return m.growth_stage.efficiency.rule_of_40
    return None


def extract_sbc_pct_revenue(m: CompanyMetrics) -> float | None:
    if m.growth_stage and m.growth_stage.dilution.sbc_as_pct_revenue is not None:
        return m.growth_stage.dilution.sbc_as_pct_revenue
    return None


def extract_share_dilution(m: CompanyMetrics) -> float | None:
    if m.growth_stage:
        return m.growth_stage.dilution.share_count_growth_1y
    return None


def extract_gross_margin_trend(m: CompanyMetrics) -> float | None:
    if m.growth_stage:
        return m.growth_stage.revenue_quality.gross_margin_trend
    return None


def extract_fcf_margin_trend(m: CompanyMetrics) -> float | None:
    if m.growth_stage:
        return m.growth_stage.cash.fcf_margin_trend
    return None


def extract_operating_leverage(m: CompanyMetrics) -> float | None:
    if m.growth_stage:
        return m.growth_stage.unit_economics.operating_leverage
    return None


# Define all metrics with their configurations
TRADITIONAL_METRICS: list[MetricConfig] = [
    # Quality metrics
    MetricConfig("roic", extract_roic, higher_is_better=True),
    MetricConfig("roe", extract_roe, higher_is_better=True),
    MetricConfig("gross_margin", extract_gross_margin, higher_is_better=True),
    MetricConfig("operating_margin", extract_operating_margin, higher_is_better=True),
    MetricConfig("fcf_margin", extract_fcf_margin, higher_is_better=True),
    # Growth metrics
    MetricConfig("revenue_growth_1y", extract_revenue_growth_1y, higher_is_better=True),
    MetricConfig("revenue_growth_3y", extract_revenue_growth_3y, higher_is_better=True),
    MetricConfig("fcf_growth_1y", extract_fcf_growth_1y, higher_is_better=True),
    # Strength metrics
    MetricConfig("current_ratio", extract_current_ratio, higher_is_better=True),
    MetricConfig("debt_to_equity", extract_debt_to_equity, higher_is_better=False),
    # Valuation metrics (lower is better for most)
    MetricConfig("pe_ratio", extract_pe_ratio, higher_is_better=False),
    MetricConfig("ev_to_ebitda", extract_ev_to_ebitda, higher_is_better=False),
    MetricConfig("fcf_yield", extract_fcf_yield, higher_is_better=True),
]

GROWTH_STAGE_METRICS: list[MetricConfig] = [
    MetricConfig("rule_of_40", extract_rule_of_40, higher_is_better=True),
    MetricConfig("gross_margin", extract_gross_margin, higher_is_better=True),
    MetricConfig("revenue_growth_1y", extract_revenue_growth_1y, higher_is_better=True),
    MetricConfig("gross_margin_trend", extract_gross_margin_trend, higher_is_better=True),
    MetricConfig("fcf_margin_trend", extract_fcf_margin_trend, higher_is_better=True),
    MetricConfig("operating_leverage", extract_operating_leverage, higher_is_better=True),
    MetricConfig("sbc_pct_revenue", extract_sbc_pct_revenue, higher_is_better=False),
    MetricConfig("share_dilution", extract_share_dilution, higher_is_better=False),
]


def calculate_all_percentiles(
    metrics_list: Sequence[CompanyMetrics],
    metric_configs: Sequence[MetricConfig] | None = None,
) -> dict[str, list[float | None]]:
    """Calculate percentile ranks for all metrics across the universe.

    Args:
        metrics_list: List of CompanyMetrics for all stocks
        metric_configs: Optional custom metric configurations

    Returns:
        Dict mapping metric name to list of percentile ranks
    """
    if metric_configs is None:
        # Use all metrics
        metric_configs = TRADITIONAL_METRICS + GROWTH_STAGE_METRICS

    result: dict[str, list[float | None]] = {}

    for config in metric_configs:
        # Extract values for this metric
        values = [config.extractor(m) for m in metrics_list]

        # Calculate percentile ranks
        percentiles = calculate_percentile_rank(
            values,
            higher_is_better=config.higher_is_better,
            winsorize_bounds=(config.winsorize_lower, config.winsorize_upper),
        )

        result[config.name] = percentiles

    return result


def get_percentile_dataframe(
    metrics_list: Sequence[CompanyMetrics],
    percentiles: dict[str, list[float | None]],
) -> pd.DataFrame:
    """Create DataFrame with tickers and percentile ranks.

    Args:
        metrics_list: List of CompanyMetrics
        percentiles: Dict from calculate_all_percentiles

    Returns:
        DataFrame with ticker column and percentile columns
    """
    data: dict[str, Any] = {
        "ticker": [m.ticker for m in metrics_list],
        "name": [m.name for m in metrics_list],
        "stage": [m.stage.stage.value for m in metrics_list],
    }

    for metric_name, pct_values in percentiles.items():
        data[f"{metric_name}_pct"] = pct_values

    return pd.DataFrame(data)
