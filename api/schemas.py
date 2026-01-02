"""Pydantic schemas for API responses."""

from datetime import date
from typing import Optional
from pydantic import BaseModel


class CompanyScore(BaseModel):
    ticker: str
    name: str
    stage: str
    composite_score: float
    quality_score: float
    growth_score: float
    strength_score: float
    valuation_score: float


class CompanyScoreWithValuation(BaseModel):
    """Extended score with detailed valuation metrics for value investing."""
    ticker: str
    name: str
    sector: Optional[str] = None
    stage: str
    composite_score: float
    quality_score: float
    growth_score: float
    strength_score: float
    valuation_score: float
    # Detailed valuation metrics
    pe_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    fcf_yield: Optional[float] = None
    earnings_yield: Optional[float] = None
    # Combined value score (quality + valuation weighted)
    value_score: Optional[float] = None
    market_cap: Optional[float] = None


class QualityMetrics(BaseModel):
    roic: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    asset_turnover: Optional[float] = None


class GrowthMetrics(BaseModel):
    revenue_growth_1y: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    earnings_growth_1y: Optional[float] = None
    earnings_cagr_3y: Optional[float] = None
    fcf_growth_1y: Optional[float] = None
    fcf_cagr_3y: Optional[float] = None


class StrengthMetrics(BaseModel):
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None


class ValuationMetrics(BaseModel):
    pe_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_sales: Optional[float] = None
    fcf_yield: Optional[float] = None
    earnings_yield: Optional[float] = None
    peg_ratio: Optional[float] = None


class StageClassification(BaseModel):
    stage: str
    confidence: float
    reasons: list[str]


class CompanyMetrics(BaseModel):
    ticker: str
    name: str
    stage: StageClassification
    quality: QualityMetrics
    growth: GrowthMetrics
    strength: StrengthMetrics
    valuation: ValuationMetrics
    market_cap: float
    current_price: float


class Quote(BaseModel):
    symbol: str
    price: float
    market_cap: float
    volume: int
    change: float
    change_percent: float
    year_high: float
    year_low: float
    pe: Optional[float] = None
    eps: Optional[float] = None


class CompanyProfile(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    sector: str
    industry: str
    market_cap: float
    description: str
    country: str
    is_etf: bool
    is_actively_trading: bool


class IncomeStatement(BaseModel):
    date: str
    revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    ebitda: float
    eps: float


class CompanyFinancials(BaseModel):
    profile: CompanyProfile
    quote: Quote
    income_statements: list[IncomeStatement]


class PriceBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class NewsArticle(BaseModel):
    title: str
    url: str
    publisher: str
    published_at: str
    summary: Optional[str] = None


class Holding(BaseModel):
    ticker: str
    shares: float
    cost_basis: float
    purchase_date: str
    tier: str
    notes: Optional[str] = None


class Position(BaseModel):
    ticker: str
    total_shares: float
    total_cost: float
    tier: str
    current_price: float
    current_value: float
    gain_loss: float
    gain_loss_pct: float
    weight_pct: float


class TierAllocation(BaseModel):
    tier: str
    target_pct: float
    actual_pct: float
    actual_value: float
    num_positions: int
    difference_pct: float
    is_underweight: bool
    is_overweight: bool


class AllocationSummary(BaseModel):
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_pct: float
    tier_allocations: list[TierAllocation]
    positions: list[Position]


class BuyRecommendation(BaseModel):
    ticker: str
    amount: float
    shares_estimate: float
    tier: str
    score: float
    reason: str
    current_price: float
    current_weight_pct: float
    new_weight_pct: float


class DeploymentPlan(BaseModel):
    available_capital: float
    total_deployed: float
    remaining_cash: float
    recommendations: list[BuyRecommendation]
    reasoning: list[str]


class CacheStats(BaseModel):
    valid_count: int
    expired_count: int
    total_size_mb: float
    ttl_hours: float


class ScoreRequest(BaseModel):
    tickers: list[str]


class DeployRequest(BaseModel):
    amount: float
