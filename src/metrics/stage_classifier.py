"""Company lifecycle stage classifier.

Classifies companies into stages to determine which metrics are most
appropriate for evaluation:

- MATURE: FCF positive, low growth (<10%). Use traditional value metrics.
- COMPOUNDER: FCF positive, high growth (>=10%). Best of both worlds.
- GROWTH: FCF negative but high gross margin (>40%). Use growth metrics.
- SPECULATIVE: Doesn't fit above criteria. Needs manual review.
"""

from dataclasses import dataclass
from typing import Sequence

from src.data.models import CashFlowStatement, CompanyStage, IncomeStatement

from .traditional import calculate_yoy_growth


@dataclass
class StageClassification:
    """Result of stage classification."""

    stage: CompanyStage
    confidence: float  # 0.0 to 1.0
    reasons: list[str]

    # Key metrics used for classification
    fcf_positive: bool | None = None
    revenue_growth: float | None = None
    gross_margin: float | None = None
    fcf_margin: float | None = None


# Classification thresholds
GROWTH_THRESHOLD = 0.10  # 10% revenue growth divides low/high growth
GROSS_MARGIN_THRESHOLD = 0.40  # 40% gross margin for growth companies
FCF_MARGIN_THRESHOLD = 0.05  # 5% FCF margin for healthy profitability


def classify_stage(
    income_statements: Sequence[IncomeStatement],
    cashflows: Sequence[CashFlowStatement],
) -> StageClassification:
    """Classify company into lifecycle stage.

    Classification logic:
    1. Calculate key metrics (FCF, revenue growth, gross margin)
    2. Apply decision tree:
       - FCF positive + growth <10% → MATURE
       - FCF positive + growth >=10% → COMPOUNDER
       - FCF negative + gross margin >40% → GROWTH
       - Otherwise → SPECULATIVE

    Args:
        income_statements: Income statements (newest first)
        cashflows: Cash flow statements (newest first)

    Returns:
        StageClassification with stage, confidence, and reasoning
    """
    reasons: list[str] = []
    confidence = 0.5  # Start neutral

    # Extract key metrics
    fcf_positive: bool | None = None
    revenue_growth: float | None = None
    gross_margin: float | None = None
    fcf_margin: float | None = None

    # FCF check
    if cashflows:
        latest_cf = cashflows[0]
        if latest_cf.free_cash_flow is not None:
            fcf_positive = latest_cf.free_cash_flow > 0

            # FCF margin
            if income_statements:
                latest_income = income_statements[0]
                if latest_income.revenue and latest_income.revenue > 0:
                    fcf_margin = latest_cf.free_cash_flow / latest_income.revenue

    # Revenue growth (1-year)
    if len(income_statements) >= 2:
        current = income_statements[0]
        prior = income_statements[1]
        revenue_growth = calculate_yoy_growth(current.revenue, prior.revenue)

    # Gross margin
    if income_statements:
        latest = income_statements[0]
        if latest.revenue and latest.revenue > 0 and latest.gross_profit:
            gross_margin = latest.gross_profit / latest.revenue

    # Decision tree
    stage = CompanyStage.SPECULATIVE

    if fcf_positive is None:
        reasons.append("Unable to determine FCF (insufficient data)")
        confidence = 0.2
    elif fcf_positive:
        reasons.append(f"FCF positive (margin: {fcf_margin*100:.1f}%)" if fcf_margin else "FCF positive")
        confidence += 0.2

        if revenue_growth is not None:
            if revenue_growth >= GROWTH_THRESHOLD:
                stage = CompanyStage.COMPOUNDER
                reasons.append(f"Revenue growth {revenue_growth*100:.1f}% >= {GROWTH_THRESHOLD*100:.0f}% threshold")
                confidence += 0.2

                # Higher confidence if really growing
                if revenue_growth >= 0.20:
                    confidence += 0.1
                    reasons.append("Strong growth (>20%)")
            else:
                stage = CompanyStage.MATURE
                reasons.append(f"Revenue growth {revenue_growth*100:.1f}% < {GROWTH_THRESHOLD*100:.0f}% threshold")
                confidence += 0.2

                # Higher confidence with good FCF margin
                if fcf_margin and fcf_margin >= FCF_MARGIN_THRESHOLD:
                    confidence += 0.1
                    reasons.append(f"Healthy FCF margin (>{FCF_MARGIN_THRESHOLD*100:.0f}%)")
        else:
            # FCF positive but unknown growth
            stage = CompanyStage.MATURE
            reasons.append("Growth unknown, defaulting to MATURE due to positive FCF")
            confidence = 0.4

    else:  # FCF negative
        reasons.append("FCF negative")

        if gross_margin is not None:
            if gross_margin >= GROSS_MARGIN_THRESHOLD:
                stage = CompanyStage.GROWTH
                reasons.append(f"Gross margin {gross_margin*100:.1f}% >= {GROSS_MARGIN_THRESHOLD*100:.0f}% threshold")
                confidence += 0.2

                # Higher confidence if growing revenue
                if revenue_growth is not None and revenue_growth >= GROWTH_THRESHOLD:
                    confidence += 0.1
                    reasons.append(f"Growing revenue ({revenue_growth*100:.1f}%)")

                # Check if improving FCF
                if fcf_margin is not None and len(cashflows) >= 2:
                    prior_cf = cashflows[1]
                    if (
                        prior_cf.free_cash_flow is not None
                        and income_statements
                        and len(income_statements) >= 2
                    ):
                        prior_income = income_statements[1]
                        if prior_income.revenue and prior_income.revenue > 0:
                            prior_fcf_margin = prior_cf.free_cash_flow / prior_income.revenue
                            if fcf_margin > prior_fcf_margin:
                                confidence += 0.1
                                reasons.append("FCF margin improving")
            else:
                stage = CompanyStage.SPECULATIVE
                reasons.append(f"Gross margin {gross_margin*100:.1f}% < {GROSS_MARGIN_THRESHOLD*100:.0f}% threshold")
                reasons.append("FCF negative with low gross margin - needs manual review")
                confidence = 0.3
        else:
            stage = CompanyStage.SPECULATIVE
            reasons.append("Gross margin unknown")
            confidence = 0.3

    # Cap confidence
    confidence = min(confidence, 1.0)

    return StageClassification(
        stage=stage,
        confidence=confidence,
        reasons=reasons,
        fcf_positive=fcf_positive,
        revenue_growth=revenue_growth,
        gross_margin=gross_margin,
        fcf_margin=fcf_margin,
    )


def get_stage_description(stage: CompanyStage) -> str:
    """Get human-readable description of stage.

    Args:
        stage: Company stage enum

    Returns:
        Description string
    """
    descriptions = {
        CompanyStage.MATURE: (
            "Mature company with positive free cash flow and modest growth. "
            "Evaluate using traditional value metrics: ROIC, FCF yield, dividend yield, P/E."
        ),
        CompanyStage.COMPOUNDER: (
            "Quality compounder with positive FCF and strong growth. "
            "Best of both worlds - evaluate with blend of growth and value metrics."
        ),
        CompanyStage.GROWTH: (
            "High-growth company reinvesting for expansion. FCF may be negative but "
            "strong gross margins indicate unit economics potential. "
            "Evaluate using Rule of 40, revenue growth, gross margin trends."
        ),
        CompanyStage.SPECULATIVE: (
            "Company doesn't fit standard categories. May be turnaround, "
            "early-stage, or challenged business. Requires manual analysis "
            "before investment consideration."
        ),
    }
    return descriptions.get(stage, "Unknown stage")


def get_recommended_weights(stage: CompanyStage) -> dict[str, float]:
    """Get recommended scoring weights for each stage.

    Args:
        stage: Company stage enum

    Returns:
        Dict mapping metric category to weight (sums to 1.0)
    """
    weights = {
        CompanyStage.MATURE: {
            "quality": 0.40,
            "growth": 0.15,
            "strength": 0.25,
            "valuation": 0.20,
        },
        CompanyStage.COMPOUNDER: {
            "quality": 0.30,
            "growth": 0.30,
            "strength": 0.20,
            "valuation": 0.20,
        },
        CompanyStage.GROWTH: {
            "revenue_quality": 0.30,
            "unit_economics": 0.25,
            "cash_runway": 0.20,
            "dilution": 0.15,
            "efficiency": 0.10,
        },
        CompanyStage.SPECULATIVE: {
            # Equal weights - no strong prior
            "quality": 0.25,
            "growth": 0.25,
            "strength": 0.25,
            "valuation": 0.25,
        },
    }
    return weights.get(stage, weights[CompanyStage.SPECULATIVE])
