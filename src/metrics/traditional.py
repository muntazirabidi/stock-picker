"""Traditional financial metrics for established companies.

These metrics are most appropriate for mature, profitable companies.
For high-growth companies, see growth_stage.py.
"""

from dataclasses import dataclass
from typing import Sequence

from src.data.models import BalanceSheet, CashFlowStatement, IncomeStatement, KeyMetrics


@dataclass
class QualityMetrics:
    """Quality/profitability metrics."""

    roic: float | None = None  # Return on Invested Capital
    roe: float | None = None  # Return on Equity
    roa: float | None = None  # Return on Assets
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None
    fcf_margin: float | None = None  # FCF / Revenue
    asset_turnover: float | None = None  # Revenue / Assets


@dataclass
class GrowthMetrics:
    """Growth metrics."""

    revenue_growth_1y: float | None = None
    revenue_growth_3y_cagr: float | None = None
    revenue_growth_5y_cagr: float | None = None
    earnings_growth_1y: float | None = None
    earnings_growth_3y_cagr: float | None = None
    fcf_growth_1y: float | None = None
    fcf_growth_3y_cagr: float | None = None


@dataclass
class StrengthMetrics:
    """Financial strength/health metrics."""

    current_ratio: float | None = None
    quick_ratio: float | None = None
    debt_to_equity: float | None = None
    debt_to_ebitda: float | None = None
    interest_coverage: float | None = None
    cash_to_debt: float | None = None
    fcf_to_debt: float | None = None


@dataclass
class ValuationMetrics:
    """Valuation metrics."""

    pe_ratio: float | None = None
    ps_ratio: float | None = None
    pb_ratio: float | None = None
    ev_to_ebitda: float | None = None
    ev_to_sales: float | None = None
    fcf_yield: float | None = None
    earnings_yield: float | None = None
    peg_ratio: float | None = None


@dataclass
class TraditionalMetrics:
    """All traditional metrics combined."""

    quality: QualityMetrics
    growth: GrowthMetrics
    strength: StrengthMetrics
    valuation: ValuationMetrics


def calculate_cagr(start_value: float, end_value: float, years: int) -> float | None:
    """Calculate Compound Annual Growth Rate.

    Args:
        start_value: Starting value (older)
        end_value: Ending value (newer)
        years: Number of years between values

    Returns:
        CAGR as decimal (0.10 = 10%) or None if invalid
    """
    if years <= 0 or start_value <= 0 or end_value <= 0:
        return None

    try:
        return (end_value / start_value) ** (1 / years) - 1
    except (ZeroDivisionError, ValueError):
        return None


def calculate_yoy_growth(current: float | None, previous: float | None) -> float | None:
    """Calculate year-over-year growth rate.

    Args:
        current: Current period value
        previous: Previous period value

    Returns:
        Growth rate as decimal or None if invalid
    """
    if current is None or previous is None or previous == 0:
        return None

    return (current - previous) / abs(previous)


def calculate_roic(
    operating_income: float | None,
    tax_rate: float,
    total_debt: float | None,
    total_equity: float | None,
    cash: float | None,
) -> float | None:
    """Calculate Return on Invested Capital.

    ROIC = NOPAT / Invested Capital
    NOPAT = Operating Income * (1 - Tax Rate)
    Invested Capital = Total Debt + Total Equity - Cash

    Args:
        operating_income: Operating income (EBIT)
        tax_rate: Effective tax rate (decimal)
        total_debt: Total debt
        total_equity: Total stockholders' equity
        cash: Cash and equivalents

    Returns:
        ROIC as decimal or None if invalid
    """
    if operating_income is None:
        return None

    total_debt = total_debt or 0
    total_equity = total_equity or 0
    cash = cash or 0

    invested_capital = total_debt + total_equity - cash

    if invested_capital <= 0:
        return None

    nopat = operating_income * (1 - tax_rate)
    return nopat / invested_capital


def calculate_quality_metrics(
    income: IncomeStatement | None,
    balance: BalanceSheet | None,
    cashflow: CashFlowStatement | None,
    key_metrics: KeyMetrics | None,
) -> QualityMetrics:
    """Calculate quality/profitability metrics.

    Args:
        income: Latest income statement
        balance: Latest balance sheet
        cashflow: Latest cash flow statement
        key_metrics: Latest key metrics (for pre-calculated values)

    Returns:
        QualityMetrics dataclass
    """
    metrics = QualityMetrics()

    # Use pre-calculated metrics if available
    if key_metrics:
        metrics.roe = key_metrics.roe
        metrics.roic = key_metrics.roic

    # Calculate from statements
    if income:
        revenue = income.revenue
        if revenue and revenue > 0:
            if income.gross_profit:
                metrics.gross_margin = income.gross_profit / revenue
            if income.operating_income:
                metrics.operating_margin = income.operating_income / revenue
            if income.net_income:
                metrics.net_margin = income.net_income / revenue

    # FCF margin
    if cashflow and income and income.revenue and income.revenue > 0:
        if cashflow.free_cash_flow:
            metrics.fcf_margin = cashflow.free_cash_flow / income.revenue

    # Calculate ROIC if not available
    if metrics.roic is None and income and balance:
        # Estimate tax rate from income statement
        tax_rate = 0.21  # Default to US corporate rate
        if income.net_income and income.operating_income and income.operating_income > 0:
            implied_tax = 1 - (income.net_income / income.operating_income)
            if 0 < implied_tax < 0.5:
                tax_rate = implied_tax

        metrics.roic = calculate_roic(
            operating_income=income.operating_income,
            tax_rate=tax_rate,
            total_debt=balance.total_debt,
            total_equity=balance.total_equity,
            cash=balance.cash_and_equivalents,
        )

    # Asset turnover
    if income and balance and balance.total_assets and balance.total_assets > 0:
        if income.revenue:
            metrics.asset_turnover = income.revenue / balance.total_assets

    return metrics


def calculate_growth_metrics(
    income_statements: Sequence[IncomeStatement],
    cashflows: Sequence[CashFlowStatement],
) -> GrowthMetrics:
    """Calculate growth metrics from historical data.

    Args:
        income_statements: Income statements (newest first)
        cashflows: Cash flow statements (newest first)

    Returns:
        GrowthMetrics dataclass
    """
    metrics = GrowthMetrics()

    if len(income_statements) >= 2:
        current = income_statements[0]
        prior = income_statements[1]

        # 1-year revenue growth
        metrics.revenue_growth_1y = calculate_yoy_growth(
            current.revenue, prior.revenue
        )

        # 1-year earnings growth
        metrics.earnings_growth_1y = calculate_yoy_growth(
            current.net_income, prior.net_income
        )

    # 3-year CAGR
    if len(income_statements) >= 4:
        newest = income_statements[0]
        oldest = income_statements[3]  # 3 years ago

        if newest.revenue and oldest.revenue:
            metrics.revenue_growth_3y_cagr = calculate_cagr(
                oldest.revenue, newest.revenue, 3
            )

        if newest.net_income and oldest.net_income:
            # Only calculate if both positive (CAGR undefined for negative)
            if newest.net_income > 0 and oldest.net_income > 0:
                metrics.earnings_growth_3y_cagr = calculate_cagr(
                    oldest.net_income, newest.net_income, 3
                )

    # 5-year CAGR
    if len(income_statements) >= 6:
        newest = income_statements[0]
        oldest = income_statements[5]  # 5 years ago

        if newest.revenue and oldest.revenue:
            metrics.revenue_growth_5y_cagr = calculate_cagr(
                oldest.revenue, newest.revenue, 5
            )

    # FCF growth
    if len(cashflows) >= 2:
        current_cf = cashflows[0]
        prior_cf = cashflows[1]

        metrics.fcf_growth_1y = calculate_yoy_growth(
            current_cf.free_cash_flow, prior_cf.free_cash_flow
        )

    if len(cashflows) >= 4:
        newest_cf = cashflows[0]
        oldest_cf = cashflows[3]

        if (
            newest_cf.free_cash_flow
            and oldest_cf.free_cash_flow
            and newest_cf.free_cash_flow > 0
            and oldest_cf.free_cash_flow > 0
        ):
            metrics.fcf_growth_3y_cagr = calculate_cagr(
                oldest_cf.free_cash_flow, newest_cf.free_cash_flow, 3
            )

    return metrics


def calculate_strength_metrics(
    income: IncomeStatement | None,
    balance: BalanceSheet | None,
    cashflow: CashFlowStatement | None,
    key_metrics: KeyMetrics | None,
) -> StrengthMetrics:
    """Calculate financial strength metrics.

    Args:
        income: Latest income statement
        balance: Latest balance sheet
        cashflow: Latest cash flow statement
        key_metrics: Latest key metrics

    Returns:
        StrengthMetrics dataclass
    """
    metrics = StrengthMetrics()

    # Use pre-calculated if available
    if key_metrics:
        metrics.current_ratio = key_metrics.current_ratio
        metrics.debt_to_equity = key_metrics.debt_to_equity
        metrics.interest_coverage = key_metrics.interest_coverage

    if balance:
        # Current ratio
        if (
            metrics.current_ratio is None
            and balance.total_current_assets
            and balance.total_current_liabilities
            and balance.total_current_liabilities > 0
        ):
            metrics.current_ratio = (
                balance.total_current_assets / balance.total_current_liabilities
            )

        # Quick ratio (current assets - inventory) / current liabilities
        if balance.total_current_liabilities and balance.total_current_liabilities > 0:
            current_assets = balance.total_current_assets or 0
            inventory = balance.inventory or 0
            metrics.quick_ratio = (
                current_assets - inventory
            ) / balance.total_current_liabilities

        # Debt to equity
        if (
            metrics.debt_to_equity is None
            and balance.total_debt
            and balance.total_equity
            and balance.total_equity > 0
        ):
            metrics.debt_to_equity = balance.total_debt / balance.total_equity

        # Cash to debt
        if balance.cash_and_equivalents and balance.total_debt and balance.total_debt > 0:
            metrics.cash_to_debt = balance.cash_and_equivalents / balance.total_debt

    # Debt to EBITDA
    if income and balance and income.ebitda and income.ebitda > 0 and balance.total_debt:
        metrics.debt_to_ebitda = balance.total_debt / income.ebitda

    # FCF to debt
    if cashflow and balance and balance.total_debt and balance.total_debt > 0:
        if cashflow.free_cash_flow:
            metrics.fcf_to_debt = cashflow.free_cash_flow / balance.total_debt

    return metrics


def calculate_valuation_metrics(
    key_metrics: KeyMetrics | None,
    income: IncomeStatement | None,
    cashflow: CashFlowStatement | None,
    market_cap: float | None,
    growth_3y: float | None,
) -> ValuationMetrics:
    """Calculate valuation metrics.

    Args:
        key_metrics: Latest key metrics (has most valuation ratios)
        income: Latest income statement
        cashflow: Latest cash flow statement
        market_cap: Current market cap
        growth_3y: 3-year earnings growth for PEG calculation

    Returns:
        ValuationMetrics dataclass
    """
    metrics = ValuationMetrics()

    if key_metrics:
        metrics.pe_ratio = key_metrics.pe_ratio
        metrics.ps_ratio = key_metrics.price_to_sales
        metrics.pb_ratio = key_metrics.price_to_book
        metrics.ev_to_ebitda = key_metrics.ev_to_ebitda
        metrics.ev_to_sales = key_metrics.ev_to_sales
        metrics.fcf_yield = key_metrics.fcf_yield
        metrics.earnings_yield = key_metrics.earnings_yield
        metrics.peg_ratio = key_metrics.peg_ratio

    # Calculate FCF yield if not available
    if metrics.fcf_yield is None and market_cap and market_cap > 0 and cashflow:
        if cashflow.free_cash_flow:
            metrics.fcf_yield = cashflow.free_cash_flow / market_cap

    # Calculate earnings yield if not available
    if metrics.earnings_yield is None and market_cap and market_cap > 0 and income:
        if income.net_income:
            metrics.earnings_yield = income.net_income / market_cap

    # Calculate PEG if we have PE and growth
    if metrics.peg_ratio is None and metrics.pe_ratio and growth_3y:
        growth_pct = growth_3y * 100  # Convert to percentage
        if growth_pct > 0:
            metrics.peg_ratio = metrics.pe_ratio / growth_pct

    return metrics


def calculate_traditional_metrics(
    income_statements: Sequence[IncomeStatement],
    balance_sheets: Sequence[BalanceSheet],
    cashflows: Sequence[CashFlowStatement],
    key_metrics: Sequence[KeyMetrics],
    market_cap: float | None = None,
) -> TraditionalMetrics:
    """Calculate all traditional metrics.

    Args:
        income_statements: Income statements (newest first)
        balance_sheets: Balance sheets (newest first)
        cashflows: Cash flow statements (newest first)
        key_metrics: Key metrics (newest first)
        market_cap: Current market cap

    Returns:
        TraditionalMetrics with all calculated metrics
    """
    latest_income = income_statements[0] if income_statements else None
    latest_balance = balance_sheets[0] if balance_sheets else None
    latest_cashflow = cashflows[0] if cashflows else None
    latest_metrics = key_metrics[0] if key_metrics else None

    # Calculate growth first (needed for PEG)
    growth = calculate_growth_metrics(income_statements, cashflows)

    quality = calculate_quality_metrics(
        latest_income, latest_balance, latest_cashflow, latest_metrics
    )

    strength = calculate_strength_metrics(
        latest_income, latest_balance, latest_cashflow, latest_metrics
    )

    valuation = calculate_valuation_metrics(
        latest_metrics,
        latest_income,
        latest_cashflow,
        market_cap,
        growth.earnings_growth_3y_cagr,
    )

    return TraditionalMetrics(
        quality=quality,
        growth=growth,
        strength=strength,
        valuation=valuation,
    )
