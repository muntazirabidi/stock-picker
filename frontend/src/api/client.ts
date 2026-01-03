import type {
  CompanyProfile,
  CompanyScore,
  CompanyScoreWithValuation,
  CompanyMetrics,
  CompanyFinancials,
  PriceBar,
  TechnicalIndicator,
  NewsArticle,
  AllocationSummary,
  Holding,
  DeploymentPlan,
  CacheStats,
  UniverseType,
} from '@/types'

const API_BASE = '/api'

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Universe endpoints
export async function getUniverseTickers(type: UniverseType): Promise<string[]> {
  return fetchApi<string[]>(`/universe/tickers?type=${type}`)
}

export async function scoreUniverse(tickers: string[]): Promise<CompanyScore[]> {
  return fetchApi<CompanyScore[]>('/universe/score', {
    method: 'POST',
    body: JSON.stringify({ tickers }),
  })
}

export async function scoreUniverseWithValuation(tickers: string[]): Promise<CompanyScoreWithValuation[]> {
  return fetchApi<CompanyScoreWithValuation[]>('/universe/score-with-valuation', {
    method: 'POST',
    body: JSON.stringify({ tickers }),
  })
}

// Company endpoints
export async function getCompanyProfile(ticker: string): Promise<CompanyProfile> {
  return fetchApi<CompanyProfile>(`/company/${ticker}/profile`)
}

export async function getCompanyFinancials(ticker: string): Promise<CompanyFinancials> {
  return fetchApi<CompanyFinancials>(`/company/${ticker}/financials`)
}

export async function getCompanyMetrics(ticker: string): Promise<CompanyMetrics> {
  return fetchApi<CompanyMetrics>(`/company/${ticker}/metrics`)
}

export async function getCompanyScore(ticker: string): Promise<CompanyScore> {
  return fetchApi<CompanyScore>(`/company/${ticker}/score`)
}

export async function getPriceHistory(
  ticker: string,
  period: '1M' | '1Y' | '2Y' | '5Y' = '1Y'
): Promise<PriceBar[]> {
  return fetchApi<PriceBar[]>(`/company/${ticker}/price-history?period=${period}`)
}

export async function getTechnicalIndicators(
  ticker: string,
  indicators: string[] = ['sma50', 'sma200', 'rsi']
): Promise<Record<string, TechnicalIndicator[]>> {
  const params = indicators.join(',')
  return fetchApi<Record<string, TechnicalIndicator[]>>(
    `/company/${ticker}/technical?indicators=${params}`
  )
}

export async function getCompanyNews(ticker: string, limit = 10): Promise<NewsArticle[]> {
  return fetchApi<NewsArticle[]>(`/company/${ticker}/news?limit=${limit}`)
}

// Portfolio endpoints
export async function getPortfolioHoldings(): Promise<Holding[]> {
  return fetchApi<Holding[]>('/portfolio/holdings')
}

export async function getPortfolioAllocation(): Promise<AllocationSummary> {
  return fetchApi<AllocationSummary>('/portfolio/allocation')
}

export async function addHolding(holding: Omit<Holding, 'id'>): Promise<Holding> {
  return fetchApi<Holding>('/portfolio/holdings', {
    method: 'POST',
    body: JSON.stringify(holding),
  })
}

export async function deleteHolding(ticker: string): Promise<void> {
  await fetchApi<void>(`/portfolio/holdings/${ticker}`, {
    method: 'DELETE',
  })
}

export async function deployCapital(amount: number): Promise<DeploymentPlan> {
  return fetchApi<DeploymentPlan>('/portfolio/deploy', {
    method: 'POST',
    body: JSON.stringify({ amount }),
  })
}

// System endpoints
export async function getCacheStats(): Promise<CacheStats> {
  return fetchApi<CacheStats>('/system/cache-stats')
}

export async function clearCache(): Promise<void> {
  await fetchApi<void>('/system/clear-cache', { method: 'POST' })
}

// Progress tracking
export interface ScoringProgress {
  is_running: boolean
  current: number
  total: number
  current_ticker: string
  processed: number
  failed: number
  started_at: number | null
  elapsed_seconds: number | null
}

export async function getScoringProgress(): Promise<ScoringProgress> {
  return fetchApi<ScoringProgress>('/universe/progress')
}
