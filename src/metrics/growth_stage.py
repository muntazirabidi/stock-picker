"""Growth-stage metrics for high-growth companies.

These metrics are designed for companies that may not yet be profitable
but show strong growth characteristics. Traditional metrics like P/E
or ROIC are often misleading for these companies.
"""

from dataclasses import dataclass
from typing import Sequence

from src.data.models import BalanceSheet, CashFlowStatement, IncomeStatement

from .traditional import calculate_cagr, calculate_yoy_growth


@dataclass
class RevenueQualityMetrics:
    """Revenue quality and growth metrics."""

    revenue_growth_1y: float | None = None
    revenue_growth_3y_cagr: float | None = None
    gross_margin: float | None = None
    gross_margin_trend: float | None = None  # Change in gross margin over 3 years
    revenue_per_employee: float | None = None  # If available


@dataclass
class UnitEconomicsMetrics:
    """Unit economics and efficiency metrics."""

    sga_as_pct_revenue: float | None = None  # SG&A / Revenue
    sga_trend: float | None = None  # Change in SG&A% over 3 years (negative = improving)
    rd_as_pct_revenue: float | None = None  # R&D / Revenue
    operating_leverage: float | None = None  # Revenue growth - OpEx growth


@dataclass
class CashMetrics:
    """Cash and runway metrics for growth companies."""

    operating_cf_positive: bool | None = None
    fcf_positive: bool | None = None
    fcf_margin: float | None = None
    fcf_margin_trend: float | None = None  # Improvement over 3 years
    cash_runway_years: float | None = None  # Cash / Annual burn
    cash_as_pct_assets: float | None = None


@dataclass
class DilutionMetrics:
    """Share dilution and SBC metrics."""

    share_count_growth_1y: float | None = None
    share_count_growth_3y_cagr: float | None = None
    sbc_as_pct_revenue: float | None = None
    sbc_trend: float | None = None  # Change over 3 years


@dataclass
class GrowthEfficiencyMetrics:
    """Combined growth efficiency metrics."""

    rule_of_40: float | None = None  # Revenue growth % + FCF margin %
    magic_number: float | None = None  # Net new ARR / S&M spend (if SaaS)
    burn_multiple: float | None = None  # Net burn / Net new ARR


@dataclass
class GrowthStageMetrics:
    """All growth-stage metrics combined."""

    revenue_quality: RevenueQualityMetrics
    unit_economics: UnitEconomicsMetrics
    cash: CashMetrics
    dilution: DilutionMetrics
    efficiency: GrowthEfficiencyMetrics


def calculate_rule_of_40(
    revenue_growth: float | None, fcf_margin: float | None
) -> float | None:
    """Calculate Rule of 40 score.

    Rule of 40 = Revenue Growth % + FCF Margin %
    A score >= 40 is considered healthy for growth companies.

    Args:
        revenue_growth: Revenue growth rate as decimal (0.25 = 25%)
        fcf_margin: FCF margin as decimal (0.15 = 15%)

    Returns:
        Rule of 40 score (40 = healthy threshold) or None
    """
    if revenue_growth is None or fcf_margin is None:
        return None

    # Convert to percentages and add
    return (revenue_growth * 100) + (fcf_margin * 100)


def calculate_revenue_quality(
    income_statements: Sequence[IncomeStatement],
) -> RevenueQualityMetrics:
    """Calculate revenue quality metrics.

    Args:
        income_statements: Income statements (newest first)

    Returns:
        RevenueQualityMetrics dataclass
    """
    metrics = RevenueQualityMetrics()

    if not income_statements:
        return metrics

    latest = income_statements[0]

    # Current gross margin
    if latest.revenue and latest.revenue > 0 and latest.gross_profit:
        metrics.gross_margin = latest.gross_profit / latest.revenue

    # 1-year revenue growth
    if len(income_statements) >= 2:
        prior = income_statements[1]
        metrics.revenue_growth_1y = calculate_yoy_growth(
            latest.revenue, prior.revenue
        )

    # 3-year revenue CAGR
    if len(income_statements) >= 4:
        oldest = income_statements[3]
        if latest.revenue and oldest.revenue:
            metrics.revenue_growth_3y_cagr = calculate_cagr(
                oldest.revenue, latest.revenue, 3
            )

    # Gross margin trend (3-year change)
    if len(income_statements) >= 4:
        oldest = income_statements[3]
        if (
            oldest.revenue
            and oldest.revenue > 0
            and oldest.gross_profit
            and metrics.gross_margin is not None
        ):
            old_margin = oldest.gross_profit / oldest.revenue
            metrics.gross_margin_trend = metrics.gross_margin - old_margin

    return metrics


def calculate_unit_economics(
    income_statements: Sequence[IncomeStatement],
) -> UnitEconomicsMetrics:
    """Calculate unit economics metrics.

    Args:
        income_statements: Income statements (newest first)

    Returns:
        UnitEconomicsMetrics dataclass
    """
    metrics = UnitEconomicsMetrics()

    if not income_statements:
        return metrics

    latest = income_statements[0]
    revenue = latest.revenue

    if not revenue or revenue <= 0:
        return metrics

    # Current SG&A as % of revenue
    if latest.sga_expenses:
        metrics.sga_as_pct_revenue = latest.sga_expenses / revenue

    # Current R&D as % of revenue
    if latest.research_and_development:
        metrics.rd_as_pct_revenue = latest.research_and_development / revenue

    # SG&A trend (3-year improvement)
    if len(income_statements) >= 4 and metrics.sga_as_pct_revenue is not None:
        oldest = income_statements[3]
        if oldest.revenue and oldest.revenue > 0 and oldest.sga_expenses:
            old_sga_pct = oldest.sga_expenses / oldest.revenue
            # Negative means improving (lower SG&A%)
            metrics.sga_trend = metrics.sga_as_pct_revenue - old_sga_pct

    # Operating leverage: compare revenue growth to opex growth
    if len(income_statements) >= 2:
        prior = income_statements[1]
        revenue_growth = calculate_yoy_growth(latest.revenue, prior.revenue)

        # Calculate opex (SG&A + R&D)
        latest_opex = (latest.sga_expenses or 0) + (latest.research_and_development or 0)
        prior_opex = (prior.sga_expenses or 0) + (prior.research_and_development or 0)
        opex_growth = calculate_yoy_growth(latest_opex, prior_opex)

        if revenue_growth is not None and opex_growth is not None:
            # Positive = revenue growing faster than expenses
            metrics.operating_leverage = revenue_growth - opex_growth

    return metrics


def calculate_cash_metrics(
    income_statements: Sequence[IncomeStatement],
    cashflows: Sequence[CashFlowStatement],
    balance_sheets: Sequence[BalanceSheet],
) -> CashMetrics:
    """Calculate cash and runway metrics.

    Args:
        income_statements: Income statements (newest first)
        cashflows: Cash flow statements (newest first)
        balance_sheets: Balance sheets (newest first)

    Returns:
        CashMetrics dataclass
    """
    metrics = CashMetrics()

    if not cashflows:
        return metrics

    latest_cf = cashflows[0]

    # Cash flow positivity
    if latest_cf.operating_cash_flow is not None:
        metrics.operating_cf_positive = latest_cf.operating_cash_flow > 0

    if latest_cf.free_cash_flow is not None:
        metrics.fcf_positive = latest_cf.free_cash_flow > 0

    # FCF margin
    if income_statements and latest_cf.free_cash_flow is not None:
        latest_income = income_statements[0]
        if latest_income.revenue and latest_income.revenue > 0:
            metrics.fcf_margin = latest_cf.free_cash_flow / latest_income.revenue

    # FCF margin trend
    if len(cashflows) >= 4 and len(income_statements) >= 4:
        oldest_cf = cashflows[3]
        oldest_income = income_statements[3]

        if (
            oldest_cf.free_cash_flow is not None
            and oldest_income.revenue
            and oldest_income.revenue > 0
            and metrics.fcf_margin is not None
        ):
            old_fcf_margin = oldest_cf.free_cash_flow / oldest_income.revenue
            metrics.fcf_margin_trend = metrics.fcf_margin - old_fcf_margin

    # Cash runway
    if balance_sheets:
        latest_balance = balance_sheets[0]
        cash = latest_balance.cash_and_equivalents or 0
        short_term = latest_balance.short_term_investments or 0
        total_cash = cash + short_term

        # Cash as % of assets
        if latest_balance.total_assets and latest_balance.total_assets > 0:
            metrics.cash_as_pct_assets = total_cash / latest_balance.total_assets

        # Runway calculation (if burning cash)
        if latest_cf.free_cash_flow is not None and latest_cf.free_cash_flow < 0:
            annual_burn = abs(latest_cf.free_cash_flow)
            if annual_burn > 0:
                metrics.cash_runway_years = total_cash / annual_burn

    return metrics


def calculate_dilution_metrics(
    income_statements: Sequence[IncomeStatement],
    cashflows: Sequence[CashFlowStatement],
    balance_sheets: Sequence[BalanceSheet],
) -> DilutionMetrics:
    """Calculate share dilution and SBC metrics.

    Args:
        income_statements: Income statements (newest first)
        cashflows: Cash flow statements (newest first)
        balance_sheets: Balance sheets (newest first)

    Returns:
        DilutionMetrics dataclass
    """
    metrics = DilutionMetrics()

    # Share count growth from balance sheets
    if len(balance_sheets) >= 2:
        latest = balance_sheets[0]
        prior = balance_sheets[1]

        metrics.share_count_growth_1y = calculate_yoy_growth(
            latest.common_stock_shares_outstanding,
            prior.common_stock_shares_outstanding,
        )

    if len(balance_sheets) >= 4:
        latest = balance_sheets[0]
        oldest = balance_sheets[3]

        if (
            latest.common_stock_shares_outstanding
            and oldest.common_stock_shares_outstanding
        ):
            metrics.share_count_growth_3y_cagr = calculate_cagr(
                oldest.common_stock_shares_outstanding,
                latest.common_stock_shares_outstanding,
                3,
            )

    # SBC as % of revenue
    if cashflows and income_statements:
        latest_cf = cashflows[0]
        latest_income = income_statements[0]

        if (
            latest_cf.stock_based_compensation
            and latest_income.revenue
            and latest_income.revenue > 0
        ):
            metrics.sbc_as_pct_revenue = (
                latest_cf.stock_based_compensation / latest_income.revenue
            )

    # SBC trend
    if len(cashflows) >= 4 and len(income_statements) >= 4:
        oldest_cf = cashflows[3]
        oldest_income = income_statements[3]

        if (
            oldest_cf.stock_based_compensation
            and oldest_income.revenue
            and oldest_income.revenue > 0
            and metrics.sbc_as_pct_revenue is not None
        ):
            old_sbc_pct = oldest_cf.stock_based_compensation / oldest_income.revenue
            metrics.sbc_trend = metrics.sbc_as_pct_revenue - old_sbc_pct

    return metrics


def calculate_efficiency_metrics(
    revenue_growth: float | None,
    fcf_margin: float | None,
) -> GrowthEfficiencyMetrics:
    """Calculate growth efficiency metrics.

    Args:
        revenue_growth: Revenue growth rate (decimal)
        fcf_margin: FCF margin (decimal)

    Returns:
        GrowthEfficiencyMetrics dataclass
    """
    metrics = GrowthEfficiencyMetrics()

    # Rule of 40
    metrics.rule_of_40 = calculate_rule_of_40(revenue_growth, fcf_margin)

    # Note: Magic number and burn multiple require ARR data
    # which is not available from standard financial statements.
    # These would need to be manually input or estimated.

    return metrics


def calculate_growth_stage_metrics(
    income_statements: Sequence[IncomeStatement],
    balance_sheets: Sequence[BalanceSheet],
    cashflows: Sequence[CashFlowStatement],
) -> GrowthStageMetrics:
    """Calculate all growth-stage metrics.

    Args:
        income_statements: Income statements (newest first)
        balance_sheets: Balance sheets (newest first)
        cashflows: Cash flow statements (newest first)

    Returns:
        GrowthStageMetrics with all calculated metrics
    """
    revenue_quality = calculate_revenue_quality(income_statements)
    unit_economics = calculate_unit_economics(income_statements)
    cash = calculate_cash_metrics(income_statements, cashflows, balance_sheets)
    dilution = calculate_dilution_metrics(income_statements, cashflows, balance_sheets)

    # Get values for efficiency metrics
    revenue_growth = revenue_quality.revenue_growth_1y
    fcf_margin = cash.fcf_margin

    efficiency = calculate_efficiency_metrics(revenue_growth, fcf_margin)

    return GrowthStageMetrics(
        revenue_quality=revenue_quality,
        unit_economics=unit_economics,
        cash=cash,
        dilution=dilution,
        efficiency=efficiency,
    )
