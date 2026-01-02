// Company types
export interface CompanyProfile {
  symbol: string
  company_name: string
  exchange: string
  sector: string
  industry: string
  market_cap: number
  description: string
  country: string
  is_etf: boolean
  is_actively_trading: boolean
}

export interface Quote {
  symbol: string
  price: number
  market_cap: number
  volume: number
  change: number
  change_percent: number
  year_high: number
  year_low: number
  pe: number | null
  eps: number | null
}

export interface CompanyScore {
  ticker: string
  name: string
  stage: CompanyStage
  composite_score: number
  quality_score: number
  growth_score: number
  strength_score: number
  valuation_score: number
}

export interface CompanyScoreWithValuation extends CompanyScore {
  sector: string | null
  pe_ratio: number | null
  peg_ratio: number | null
  ps_ratio: number | null
  pb_ratio: number | null
  ev_ebitda: number | null
  fcf_yield: number | null
  earnings_yield: number | null
  value_score: number | null
  market_cap: number | null
}

export type CompanyStage = 'mature' | 'compounder' | 'growth' | 'speculative'

export interface StageClassification {
  stage: CompanyStage
  confidence: number
  reasons: string[]
}

// Metrics types
export interface QualityMetrics {
  roic: number | null
  roe: number | null
  roa: number | null
  gross_margin: number | null
  operating_margin: number | null
  net_margin: number | null
  fcf_margin: number | null
  asset_turnover: number | null
}

export interface GrowthMetrics {
  revenue_growth_1y: number | null
  revenue_cagr_3y: number | null
  revenue_cagr_5y: number | null
  earnings_growth_1y: number | null
  earnings_cagr_3y: number | null
  fcf_growth_1y: number | null
  fcf_cagr_3y: number | null
}

export interface StrengthMetrics {
  current_ratio: number | null
  quick_ratio: number | null
  debt_to_equity: number | null
  interest_coverage: number | null
}

export interface ValuationMetrics {
  pe_ratio: number | null
  ps_ratio: number | null
  pb_ratio: number | null
  ev_ebitda: number | null
  ev_sales: number | null
  fcf_yield: number | null
  earnings_yield: number | null
  peg_ratio: number | null
}

export interface CompanyMetrics {
  ticker: string
  name: string
  stage: StageClassification
  quality: QualityMetrics
  growth: GrowthMetrics
  strength: StrengthMetrics
  valuation: ValuationMetrics
  market_cap: number
  current_price: number
}

// Price history types
export interface PriceBar {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface TechnicalIndicator {
  date: string
  value: number
}

// Portfolio types
export type Tier = 'tier_1' | 'tier_2' | 'tier_3'

export interface Holding {
  ticker: string
  shares: number
  cost_basis: number
  purchase_date: string
  tier: Tier
  notes: string | null
}

export interface Position {
  ticker: string
  total_shares: number
  total_cost: number
  tier: Tier
  current_price: number
  current_value: number
  gain_loss: number
  gain_loss_pct: number
  weight_pct: number
}

export interface TierAllocation {
  tier: Tier
  target_pct: number
  actual_pct: number
  actual_value: number
  num_positions: number
  difference_pct: number
  is_underweight: boolean
  is_overweight: boolean
}

export interface AllocationSummary {
  total_value: number
  total_cost: number
  total_gain_loss: number
  total_gain_loss_pct: number
  tier_allocations: TierAllocation[]
  positions: Position[]
}

export interface BuyRecommendation {
  ticker: string
  amount: number
  shares_estimate: number
  tier: Tier
  score: number
  reason: string
  current_price: number
  current_weight_pct: number
  new_weight_pct: number
}

export interface DeploymentPlan {
  available_capital: number
  total_deployed: number
  remaining_cash: number
  recommendations: BuyRecommendation[]
  reasoning: string[]
}

// News types
export interface NewsArticle {
  title: string
  url: string
  publisher: string
  published_at: string
  summary: string | null
}

// Universe types
export type UniverseType = 'sp500' | 'nasdaq100' | 'midcap' | 'smallcap' | 'all' | 'custom'

export interface UniverseStock {
  ticker: string
  name: string
  tier: Tier
  source: string
  market_cap: number | null
  sector: string | null
}

// System types
export interface CacheStats {
  valid_count: number
  expired_count: number
  total_size_mb: number
  ttl_hours: number
}

// Financial statements
export interface IncomeStatement {
  date: string
  revenue: number
  gross_profit: number
  operating_income: number
  net_income: number
  ebitda: number
  eps: number
}

export interface BalanceSheet {
  date: string
  total_assets: number
  total_liabilities: number
  total_equity: number
  total_debt: number
  cash: number
}

export interface CashFlowStatement {
  date: string
  operating_cash_flow: number
  investing_cash_flow: number
  financing_cash_flow: number
  free_cash_flow: number
  capex: number
}

export interface CompanyFinancials {
  profile: CompanyProfile
  quote: Quote
  income_statements: IncomeStatement[]
  balance_sheets: BalanceSheet[]
  cash_flows: CashFlowStatement[]
}
