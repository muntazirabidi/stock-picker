"""Metrics calculator - orchestrates all metric calculations for a company."""

from dataclasses import dataclass, field
from typing import Any

from src.data.models import CompanyFinancials, CompanyStage

from .growth_stage import GrowthStageMetrics, calculate_growth_stage_metrics
from .stage_classifier import (
    StageClassification,
    classify_stage,
    get_recommended_weights,
    get_stage_description,
)
from .traditional import TraditionalMetrics, calculate_traditional_metrics


@dataclass
class CompanyMetrics:
    """Complete metrics for a company."""

    ticker: str
    name: str | None

    # Stage classification
    stage: StageClassification

    # Metrics (one or both populated depending on stage)
    traditional: TraditionalMetrics | None = None
    growth_stage: GrowthStageMetrics | None = None

    # Recommended weights for scoring
    scoring_weights: dict[str, float] = field(default_factory=dict)

    # Market data
    market_cap: float | None = None
    current_price: float | None = None

    @property
    def stage_name(self) -> str:
        """Get stage name as string."""
        return self.stage.stage.value

    @property
    def stage_description(self) -> str:
        """Get stage description."""
        return get_stage_description(self.stage.stage)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {
            "ticker": self.ticker,
            "name": self.name,
            "stage": self.stage.stage.value,
            "stage_confidence": self.stage.confidence,
            "stage_reasons": self.stage.reasons,
            "market_cap": self.market_cap,
            "current_price": self.current_price,
        }

        # Add traditional metrics if available
        if self.traditional:
            result["quality"] = {
                "roic": self.traditional.quality.roic,
                "roe": self.traditional.quality.roe,
                "gross_margin": self.traditional.quality.gross_margin,
                "operating_margin": self.traditional.quality.operating_margin,
                "net_margin": self.traditional.quality.net_margin,
                "fcf_margin": self.traditional.quality.fcf_margin,
            }
            result["growth"] = {
                "revenue_growth_1y": self.traditional.growth.revenue_growth_1y,
                "revenue_growth_3y_cagr": self.traditional.growth.revenue_growth_3y_cagr,
                "revenue_growth_5y_cagr": self.traditional.growth.revenue_growth_5y_cagr,
                "earnings_growth_1y": self.traditional.growth.earnings_growth_1y,
                "fcf_growth_1y": self.traditional.growth.fcf_growth_1y,
            }
            result["strength"] = {
                "current_ratio": self.traditional.strength.current_ratio,
                "debt_to_equity": self.traditional.strength.debt_to_equity,
                "interest_coverage": self.traditional.strength.interest_coverage,
                "cash_to_debt": self.traditional.strength.cash_to_debt,
            }
            result["valuation"] = {
                "pe_ratio": self.traditional.valuation.pe_ratio,
                "ps_ratio": self.traditional.valuation.ps_ratio,
                "pb_ratio": self.traditional.valuation.pb_ratio,
                "ev_to_ebitda": self.traditional.valuation.ev_to_ebitda,
                "fcf_yield": self.traditional.valuation.fcf_yield,
                "peg_ratio": self.traditional.valuation.peg_ratio,
            }

        # Add growth stage metrics if available
        if self.growth_stage:
            result["revenue_quality"] = {
                "revenue_growth_1y": self.growth_stage.revenue_quality.revenue_growth_1y,
                "revenue_growth_3y_cagr": self.growth_stage.revenue_quality.revenue_growth_3y_cagr,
                "gross_margin": self.growth_stage.revenue_quality.gross_margin,
                "gross_margin_trend": self.growth_stage.revenue_quality.gross_margin_trend,
            }
            result["unit_economics"] = {
                "sga_as_pct_revenue": self.growth_stage.unit_economics.sga_as_pct_revenue,
                "sga_trend": self.growth_stage.unit_economics.sga_trend,
                "rd_as_pct_revenue": self.growth_stage.unit_economics.rd_as_pct_revenue,
                "operating_leverage": self.growth_stage.unit_economics.operating_leverage,
            }
            result["cash"] = {
                "fcf_positive": self.growth_stage.cash.fcf_positive,
                "fcf_margin": self.growth_stage.cash.fcf_margin,
                "fcf_margin_trend": self.growth_stage.cash.fcf_margin_trend,
                "cash_runway_years": self.growth_stage.cash.cash_runway_years,
            }
            result["dilution"] = {
                "share_count_growth_1y": self.growth_stage.dilution.share_count_growth_1y,
                "share_count_growth_3y_cagr": self.growth_stage.dilution.share_count_growth_3y_cagr,
                "sbc_as_pct_revenue": self.growth_stage.dilution.sbc_as_pct_revenue,
            }
            result["efficiency"] = {
                "rule_of_40": self.growth_stage.efficiency.rule_of_40,
            }

        return result

    def get_key_metrics_summary(self) -> dict[str, Any]:
        """Get summary of most important metrics based on stage."""
        stage = self.stage.stage

        if stage in (CompanyStage.MATURE, CompanyStage.COMPOUNDER):
            if self.traditional:
                return {
                    "roic": self.traditional.quality.roic,
                    "fcf_margin": self.traditional.quality.fcf_margin,
                    "revenue_growth": self.traditional.growth.revenue_growth_3y_cagr,
                    "debt_to_equity": self.traditional.strength.debt_to_equity,
                    "pe_ratio": self.traditional.valuation.pe_ratio,
                    "fcf_yield": self.traditional.valuation.fcf_yield,
                }

        elif stage == CompanyStage.GROWTH:
            if self.growth_stage:
                return {
                    "rule_of_40": self.growth_stage.efficiency.rule_of_40,
                    "revenue_growth": self.growth_stage.revenue_quality.revenue_growth_1y,
                    "gross_margin": self.growth_stage.revenue_quality.gross_margin,
                    "fcf_margin_trend": self.growth_stage.cash.fcf_margin_trend,
                    "sbc_as_pct_revenue": self.growth_stage.dilution.sbc_as_pct_revenue,
                    "cash_runway_years": self.growth_stage.cash.cash_runway_years,
                }

        # Default/speculative - mix of both
        result: dict[str, Any] = {}
        if self.traditional:
            result["gross_margin"] = self.traditional.quality.gross_margin
            result["revenue_growth"] = self.traditional.growth.revenue_growth_1y
        if self.growth_stage:
            result["rule_of_40"] = self.growth_stage.efficiency.rule_of_40

        return result


class MetricsCalculator:
    """Calculator for company metrics."""

    def calculate(self, financials: CompanyFinancials) -> CompanyMetrics:
        """Calculate all metrics for a company.

        Args:
            financials: CompanyFinancials with all financial data

        Returns:
            CompanyMetrics with calculated metrics
        """
        income = financials.income_statements
        balance = financials.balance_sheets
        cashflow = financials.cash_flows
        key_metrics = financials.key_metrics

        # Classify stage first
        stage = classify_stage(income, cashflow)

        # Get market data
        market_cap = None
        current_price = None
        if financials.quote:
            market_cap = financials.quote.market_cap
            current_price = financials.quote.price

        # Calculate appropriate metrics based on stage
        traditional: TraditionalMetrics | None = None
        growth_stage: GrowthStageMetrics | None = None

        # Always calculate traditional for mature/compounder
        if stage.stage in (CompanyStage.MATURE, CompanyStage.COMPOUNDER):
            traditional = calculate_traditional_metrics(
                income, balance, cashflow, key_metrics, market_cap
            )
            # Also calculate growth metrics for compounders
            if stage.stage == CompanyStage.COMPOUNDER:
                growth_stage = calculate_growth_stage_metrics(income, balance, cashflow)

        # Always calculate growth metrics for growth stage
        elif stage.stage == CompanyStage.GROWTH:
            growth_stage = calculate_growth_stage_metrics(income, balance, cashflow)
            # Also calculate traditional for reference
            traditional = calculate_traditional_metrics(
                income, balance, cashflow, key_metrics, market_cap
            )

        # For speculative, calculate both
        else:
            traditional = calculate_traditional_metrics(
                income, balance, cashflow, key_metrics, market_cap
            )
            growth_stage = calculate_growth_stage_metrics(income, balance, cashflow)

        # Get recommended scoring weights
        weights = get_recommended_weights(stage.stage)

        return CompanyMetrics(
            ticker=financials.ticker,
            name=financials.profile.company_name,
            stage=stage,
            traditional=traditional,
            growth_stage=growth_stage,
            scoring_weights=weights,
            market_cap=market_cap,
            current_price=current_price,
        )

    def calculate_batch(
        self, financials_list: list[CompanyFinancials]
    ) -> list[CompanyMetrics]:
        """Calculate metrics for multiple companies.

        Args:
            financials_list: List of CompanyFinancials

        Returns:
            List of CompanyMetrics
        """
        return [self.calculate(f) for f in financials_list]


def format_metric(value: float | None, format_type: str = "percent") -> str:
    """Format a metric value for display.

    Args:
        value: Metric value
        format_type: "percent", "ratio", "currency", "number"

    Returns:
        Formatted string or "N/A"
    """
    if value is None:
        return "N/A"

    if format_type == "percent":
        return f"{value * 100:.1f}%"
    elif format_type == "ratio":
        return f"{value:.2f}"
    elif format_type == "currency":
        if abs(value) >= 1e12:
            return f"${value / 1e12:.1f}T"
        elif abs(value) >= 1e9:
            return f"${value / 1e9:.1f}B"
        elif abs(value) >= 1e6:
            return f"${value / 1e6:.1f}M"
        else:
            return f"${value:,.0f}"
    else:
        return f"{value:.2f}"


def print_metrics_summary(metrics: CompanyMetrics) -> None:
    """Print a formatted summary of company metrics.

    Args:
        metrics: CompanyMetrics to display
    """
    print(f"\n{'='*60}")
    print(f"{metrics.ticker} - {metrics.name}")
    print(f"{'='*60}")

    # Stage info
    print(f"\nStage: {metrics.stage.stage.value.upper()}")
    print(f"Confidence: {metrics.stage.confidence:.0%}")
    print("Reasons:")
    for reason in metrics.stage.reasons:
        print(f"  • {reason}")

    # Market data
    if metrics.market_cap or metrics.current_price:
        print(f"\nMarket Data:")
        if metrics.current_price:
            print(f"  Price: ${metrics.current_price:.2f}")
        if metrics.market_cap:
            print(f"  Market Cap: {format_metric(metrics.market_cap, 'currency')}")

    # Key metrics based on stage
    print(f"\nKey Metrics:")
    summary = metrics.get_key_metrics_summary()
    for key, value in summary.items():
        display_key = key.replace("_", " ").title()
        if "ratio" in key.lower() or "multiple" in key.lower():
            formatted = format_metric(value, "ratio")
        elif "yield" in key.lower() or "margin" in key.lower() or "growth" in key.lower():
            formatted = format_metric(value, "percent")
        elif key == "rule_of_40":
            formatted = f"{value:.1f}" if value else "N/A"
        elif key == "cash_runway_years":
            formatted = f"{value:.1f} years" if value else "N/A"
        else:
            formatted = format_metric(value, "ratio")
        print(f"  {display_key}: {formatted}")

    print(f"\n{'='*60}")
