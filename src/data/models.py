"""Pydantic models for financial data validation."""

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Tier(str, Enum):
    """Universe tier classification."""

    TIER_1 = "tier_1"  # Established compounders
    TIER_2 = "tier_2"  # High growth
    TIER_3 = "tier_3"  # Opportunistic


class CompanyStage(str, Enum):
    """Company lifecycle stage for scoring."""

    MATURE = "mature"  # FCF positive, low growth
    COMPOUNDER = "compounder"  # FCF positive, high growth
    GROWTH = "growth"  # FCF negative, high gross margin
    SPECULATIVE = "speculative"  # Needs manual review


class CompanyProfile(BaseModel):
    """Basic company information from FMP profile endpoint."""

    symbol: str
    company_name: str = Field(alias="companyName")
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = Field(None, alias="mktCap")
    description: str | None = None
    country: str | None = None
    is_etf: bool = Field(False, alias="isEtf")
    is_actively_trading: bool = Field(True, alias="isActivelyTrading")

    class Config:
        populate_by_name = True


class IncomeStatement(BaseModel):
    """Annual income statement data."""

    date: date
    symbol: str
    period: str = "FY"

    revenue: float | None = None
    gross_profit: float | None = Field(None, alias="grossProfit")
    operating_income: float | None = Field(None, alias="operatingIncome")
    net_income: float | None = Field(None, alias="netIncome")
    ebitda: float | None = None

    # Per share
    eps: float | None = None

    # Margins (we'll calculate these too)
    gross_profit_ratio: float | None = Field(None, alias="grossProfitRatio")
    operating_income_ratio: float | None = Field(None, alias="operatingIncomeRatio")
    net_income_ratio: float | None = Field(None, alias="netIncomeRatio")

    # Expenses
    research_and_development: float | None = Field(None, alias="researchAndDevelopmentExpenses")
    sga_expenses: float | None = Field(None, alias="sellingGeneralAndAdministrativeExpenses")

    # Stock-based compensation (critical for growth companies)
    stock_based_compensation: float | None = None

    class Config:
        populate_by_name = True


class BalanceSheet(BaseModel):
    """Annual balance sheet data."""

    date: date
    symbol: str
    period: str = "FY"

    # Assets
    total_assets: float | None = Field(None, alias="totalAssets")
    total_current_assets: float | None = Field(None, alias="totalCurrentAssets")
    cash_and_equivalents: float | None = Field(None, alias="cashAndCashEquivalents")
    short_term_investments: float | None = Field(None, alias="shortTermInvestments")
    inventory: float | None = None
    total_receivables: float | None = Field(None, alias="netReceivables")

    # Liabilities
    total_liabilities: float | None = Field(None, alias="totalLiabilities")
    total_current_liabilities: float | None = Field(None, alias="totalCurrentLiabilities")
    total_debt: float | None = Field(None, alias="totalDebt")
    long_term_debt: float | None = Field(None, alias="longTermDebt")
    short_term_debt: float | None = Field(None, alias="shortTermDebt")

    # Equity
    total_equity: float | None = Field(None, alias="totalStockholdersEquity")
    retained_earnings: float | None = Field(None, alias="retainedEarnings")

    # Shares
    common_stock_shares_outstanding: float | None = Field(
        None, alias="commonStockSharesOutstanding"
    )

    class Config:
        populate_by_name = True


class CashFlowStatement(BaseModel):
    """Annual cash flow statement data."""

    date: date
    symbol: str
    period: str = "FY"

    # Operating
    operating_cash_flow: float | None = Field(None, alias="operatingCashFlow")
    net_income: float | None = Field(None, alias="netIncome")
    depreciation: float | None = Field(None, alias="depreciationAndAmortization")
    stock_based_compensation: float | None = Field(None, alias="stockBasedCompensation")

    # Investing
    capital_expenditure: float | None = Field(None, alias="capitalExpenditure")
    acquisitions: float | None = Field(None, alias="acquisitionsNet")
    investments: float | None = Field(None, alias="purchasesOfInvestments")

    # Financing
    debt_repayment: float | None = Field(None, alias="debtRepayment")
    dividends_paid: float | None = Field(None, alias="dividendsPaid")
    share_repurchases: float | None = Field(None, alias="commonStockRepurchased")
    share_issuance: float | None = Field(None, alias="commonStockIssued")

    # Free cash flow (we'll calculate if not provided)
    free_cash_flow: float | None = Field(None, alias="freeCashFlow")

    class Config:
        populate_by_name = True


class KeyMetrics(BaseModel):
    """Pre-calculated key metrics from FMP."""

    date: date
    symbol: str
    period: str = "FY"

    # Valuation
    pe_ratio: float | None = Field(None, alias="peRatio")
    price_to_sales: float | None = Field(None, alias="priceToSalesRatio")
    price_to_book: float | None = Field(None, alias="pbRatio")
    ev_to_ebitda: float | None = Field(None, alias="enterpriseValueOverEBITDA")
    ev_to_sales: float | None = Field(None, alias="evToSales")

    # Profitability
    roe: float | None = Field(None, alias="roe")
    roa: float | None = Field(None, alias="returnOnTangibleAssets")
    roic: float | None = Field(None, alias="roic")

    # Per share
    revenue_per_share: float | None = Field(None, alias="revenuePerShare")
    fcf_per_share: float | None = Field(None, alias="freeCashFlowPerShare")
    book_value_per_share: float | None = Field(None, alias="bookValuePerShare")

    # Yield
    dividend_yield: float | None = Field(None, alias="dividendYield")
    fcf_yield: float | None = Field(None, alias="freeCashFlowYield")
    earnings_yield: float | None = Field(None, alias="earningsYield")

    # Health
    current_ratio: float | None = Field(None, alias="currentRatio")
    debt_to_equity: float | None = Field(None, alias="debtToEquity")
    debt_to_assets: float | None = Field(None, alias="debtToAssets")
    interest_coverage: float | None = Field(None, alias="interestCoverage")

    # Growth (TTM based)
    peg_ratio: float | None = Field(None, alias="pegRatio")

    class Config:
        populate_by_name = True


class Quote(BaseModel):
    """Current stock quote."""

    symbol: str
    price: float
    market_cap: float | None = Field(None, alias="marketCap")
    volume: int | None = None
    avg_volume: int | None = Field(None, alias="avgVolume")
    change: float | None = None
    change_percent: float | None = Field(None, alias="changesPercentage")
    year_high: float | None = Field(None, alias="yearHigh")
    year_low: float | None = Field(None, alias="yearLow")
    pe: float | None = None
    eps: float | None = None

    class Config:
        populate_by_name = True


class UniverseStock(BaseModel):
    """Stock entry in our universe."""

    ticker: str
    name: str | None = None
    tier: Tier
    source: str  # e.g., "sp500", "midcap400", "watchlist"
    market_cap: float | None = None
    sector: str | None = None
    added_date: date | None = None
    notes: str | None = None

    @field_validator("ticker", mode="before")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()


class CompanyFinancials(BaseModel):
    """Aggregated financial data for a company."""

    profile: CompanyProfile
    income_statements: list[IncomeStatement] = []
    balance_sheets: list[BalanceSheet] = []
    cash_flows: list[CashFlowStatement] = []
    key_metrics: list[KeyMetrics] = []
    quote: Quote | None = None

    @property
    def ticker(self) -> str:
        return self.profile.symbol

    @property
    def latest_income(self) -> IncomeStatement | None:
        return self.income_statements[0] if self.income_statements else None

    @property
    def latest_balance(self) -> BalanceSheet | None:
        return self.balance_sheets[0] if self.balance_sheets else None

    @property
    def latest_cashflow(self) -> CashFlowStatement | None:
        return self.cash_flows[0] if self.cash_flows else None

    @property
    def latest_metrics(self) -> KeyMetrics | None:
        return self.key_metrics[0] if self.key_metrics else None


class Holding(BaseModel):
    """Portfolio holding record."""

    ticker: str
    shares: float
    cost_basis: float  # Total cost, not per share
    purchase_date: date
    tier: Tier
    notes: str | None = None

    @property
    def cost_per_share(self) -> float:
        return self.cost_basis / self.shares if self.shares > 0 else 0

    @field_validator("ticker", mode="before")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()
