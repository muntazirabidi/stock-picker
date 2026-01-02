"""Metrics calculation for equity research system."""

from .calculator import (
    CompanyMetrics,
    MetricsCalculator,
    format_metric,
    print_metrics_summary,
)
from .growth_stage import (
    CashMetrics,
    DilutionMetrics,
    GrowthEfficiencyMetrics,
    GrowthStageMetrics,
    RevenueQualityMetrics,
    UnitEconomicsMetrics,
    calculate_growth_stage_metrics,
    calculate_rule_of_40,
)
from .stage_classifier import (
    StageClassification,
    classify_stage,
    get_recommended_weights,
    get_stage_description,
)
from .traditional import (
    GrowthMetrics,
    QualityMetrics,
    StrengthMetrics,
    TraditionalMetrics,
    ValuationMetrics,
    calculate_cagr,
    calculate_traditional_metrics,
)

__all__ = [
    # Calculator
    "CompanyMetrics",
    "MetricsCalculator",
    "format_metric",
    "print_metrics_summary",
    # Traditional metrics
    "QualityMetrics",
    "GrowthMetrics",
    "StrengthMetrics",
    "ValuationMetrics",
    "TraditionalMetrics",
    "calculate_traditional_metrics",
    "calculate_cagr",
    # Growth stage metrics
    "RevenueQualityMetrics",
    "UnitEconomicsMetrics",
    "CashMetrics",
    "DilutionMetrics",
    "GrowthEfficiencyMetrics",
    "GrowthStageMetrics",
    "calculate_growth_stage_metrics",
    "calculate_rule_of_40",
    # Stage classifier
    "StageClassification",
    "classify_stage",
    "get_recommended_weights",
    "get_stage_description",
]
