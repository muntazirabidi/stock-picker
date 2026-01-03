import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { PriceChart } from '@/components/charts/PriceChart'
import { FinancialChart } from '@/components/charts/FinancialChart'
import { ScoreRadar } from '@/components/charts/ScoreRadar'
import {
  useCompanyProfile,
  useCompanyScore,
  useCompanyMetrics,
  useCompanyFinancials,
  usePriceHistory,
  useCompanyNews,
} from '@/hooks/useCompany'
import {
  cn,
  formatCompactNumber,
  formatPercent,
  formatNumber,
  getStageColor,
  getScoreColor,
  getChangeColor,
} from '@/lib/utils'
import { Search, TrendingUp, TrendingDown, ExternalLink, ChevronDown, ChevronUp, Building2, DollarSign, BarChart3, Percent, Calendar } from 'lucide-react'

const quickPicks = ['MSFT', 'AAPL', 'V', 'COST', 'HUBS', 'CRWD']
const periods = ['1M', '1Y', '2Y', '5Y'] as const

interface MetricRowProps {
  label: string
  value: number | null | undefined
  format?: 'percent' | 'number' | 'ratio'
  inverse?: boolean
}

function MetricRow({ label, value, format = 'percent', inverse = false }: MetricRowProps) {
  if (value === null || value === undefined) {
    return (
      <div className="flex items-center justify-between py-2 border-b last:border-0">
        <span className="text-sm">{label}</span>
        <span className="text-sm text-muted-foreground">N/A</span>
      </div>
    )
  }

  const displayValue =
    format === 'percent'
      ? formatPercent(value)
      : format === 'ratio'
      ? formatNumber(value, 2) + 'x'
      : formatNumber(value, 2)

  const isGood = inverse ? value < 0.5 : value > 0.1
  const isBad = inverse ? value > 2 : value < 0

  return (
    <div className="flex items-center justify-between py-2 border-b last:border-0">
      <span className="text-sm">{label}</span>
      <span
        className={cn(
          'text-sm font-medium',
          isGood ? 'text-success' : isBad ? 'text-error' : 'text-foreground'
        )}
      >
        {displayValue}
      </span>
    </div>
  )
}

export default function Company() {
  const { ticker: paramTicker } = useParams()
  const navigate = useNavigate()
  const [searchInput, setSearchInput] = useState('')
  const [ticker, setTicker] = useState(paramTicker || '')
  const [period, setPeriod] = useState<'1M' | '1Y' | '2Y' | '5Y'>('1Y')
  const [activeTab, setActiveTab] = useState('price')
  const [showReasons, setShowReasons] = useState(false)

  const { data: profile, isLoading: isLoadingProfile } = useCompanyProfile(ticker || undefined)
  const { data: score, isLoading: isLoadingScore } = useCompanyScore(ticker || undefined)
  const { data: metrics } = useCompanyMetrics(ticker || undefined)
  const { data: financials } = useCompanyFinancials(ticker || undefined)
  const { data: priceData, isLoading: isLoadingPrice } = usePriceHistory(ticker || undefined, period)
  const { data: news } = useCompanyNews(ticker || undefined)

  const handleSearch = () => {
    const t = searchInput.trim().toUpperCase()
    if (t) {
      setTicker(t)
      navigate(`/company/${t}`)
    }
  }

  const handleQuickPick = (t: string) => {
    setTicker(t)
    setSearchInput(t)
    navigate(`/company/${t}`)
  }

  const priceChange = priceData?.length
    ? ((priceData[priceData.length - 1].close - priceData[0].close) / priceData[0].close) * 100
    : 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-light tracking-tight">Company Analysis</h1>
        <p className="text-muted-foreground">Deep dive into individual stocks</p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-end flex-wrap">
            <div className="flex-1 min-w-64">
              <label className="text-sm font-medium mb-2 block">Ticker</label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Enter ticker symbol..."
                    className="pl-9"
                  />
                </div>
                <Button onClick={handleSearch}>Analyze</Button>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              {quickPicks.map((t) => (
                <Button
                  key={t}
                  variant={ticker === t ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleQuickPick(t)}
                >
                  {t}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Company Content */}
      {ticker && (
        <>
          {/* Header */}
          <Card>
            <CardContent className="pt-6">
              {isLoadingProfile || isLoadingScore ? (
                <div className="space-y-4">
                  <Skeleton className="h-8 w-64" />
                  <Skeleton className="h-4 w-48" />
                </div>
              ) : profile && score ? (
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-semibold">{profile.company_name}</h2>
                      <Badge
                        variant="outline"
                        className={cn('capitalize', getStageColor(score.stage))}
                      >
                        {score.stage}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground">
                      {profile.sector} • {profile.industry}
                    </p>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Composite Score</p>
                      <p className={cn('text-4xl font-bold', getScoreColor(score.composite_score))}>
                        {score.composite_score.toFixed(0)}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">Unable to load company data</p>
              )}
            </CardContent>
          </Card>

          {/* Key Metrics Bar */}
          {financials?.quote && (
            <div className="grid gap-4 md:grid-cols-5">
              <Card>
                <CardContent className="pt-4 pb-4">
                  <p className="text-sm text-muted-foreground">Price</p>
                  <div className="flex items-center gap-2">
                    <p className="text-xl font-semibold">
                      ${financials.quote.price.toFixed(2)}
                    </p>
                    <span
                      className={cn(
                        'text-sm flex items-center',
                        getChangeColor(financials.quote.change_percent)
                      )}
                    >
                      {financials.quote.change_percent > 0 ? (
                        <TrendingUp className="h-4 w-4 mr-1" />
                      ) : (
                        <TrendingDown className="h-4 w-4 mr-1" />
                      )}
                      {financials.quote.change_percent.toFixed(2)}%
                    </span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4 pb-4">
                  <p className="text-sm text-muted-foreground">Market Cap</p>
                  <p className="text-xl font-semibold">
                    {formatCompactNumber(financials.quote.market_cap)}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4 pb-4">
                  <p className="text-sm text-muted-foreground">P/E Ratio</p>
                  <p className="text-xl font-semibold">
                    {financials.quote.pe ? financials.quote.pe.toFixed(1) : 'N/A'}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4 pb-4">
                  <p className="text-sm text-muted-foreground">52W High</p>
                  <p className="text-xl font-semibold">
                    ${financials.quote.year_high.toFixed(2)}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4 pb-4">
                  <p className="text-sm text-muted-foreground">52W Low</p>
                  <p className="text-xl font-semibold">
                    ${financials.quote.year_low.toFixed(2)}
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Score Breakdown with Radar */}
          {score && (
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Radar Chart */}
              <Card className="lg:col-span-1">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Score Profile</CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <ScoreRadar
                    quality={score.quality_score}
                    growth={score.growth_score}
                    strength={score.strength_score}
                    valuation={score.valuation_score}
                    size={220}
                  />
                </CardContent>
              </Card>

              {/* Score Cards */}
              <Card className="lg:col-span-2">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center justify-between">
                    Score Breakdown
                    <span className="text-xs font-normal text-muted-foreground">
                      (Percentile vs universe)
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 sm:grid-cols-2">
                    {[
                      { label: 'Quality', value: score.quality_score, desc: 'ROIC, margins, profitability' },
                      { label: 'Growth', value: score.growth_score, desc: 'Revenue & earnings growth' },
                      { label: 'Strength', value: score.strength_score, desc: 'Balance sheet health' },
                      { label: 'Valuation', value: score.valuation_score, desc: 'P/E, FCF yield, PEG' },
                    ].map(({ label, value, desc }) => (
                      <div key={label} className="p-4 rounded-lg bg-card/50 border">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-sm font-medium">{label}</p>
                          <p className={cn('text-2xl font-bold', getScoreColor(value))}>
                            {value.toFixed(0)}
                          </p>
                        </div>
                        <Progress value={value} className="h-2 mb-2" />
                        <p className="text-xs text-muted-foreground">{desc}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Company Description */}
          {profile?.description && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  About {profile.company_name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {profile.description}
                </p>
                <div className="flex flex-wrap gap-4 mt-4 text-sm">
                  {profile.ceo && (
                    <div>
                      <span className="text-muted-foreground">CEO: </span>
                      <span className="font-medium">{profile.ceo}</span>
                    </div>
                  )}
                  {profile.employees && (
                    <div>
                      <span className="text-muted-foreground">Employees: </span>
                      <span className="font-medium">{profile.employees.toLocaleString()}</span>
                    </div>
                  )}
                  {profile.ipo_date && (
                    <div>
                      <span className="text-muted-foreground">IPO: </span>
                      <span className="font-medium">{profile.ipo_date}</span>
                    </div>
                  )}
                  {profile.website && (
                    <a
                      href={profile.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline flex items-center gap-1"
                    >
                      Website <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tabs */}
          <Card>
            <CardContent className="pt-6">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="mb-4">
                  <TabsTrigger value="price">Price</TabsTrigger>
                  <TabsTrigger value="quality">Quality</TabsTrigger>
                  <TabsTrigger value="growth">Growth</TabsTrigger>
                  <TabsTrigger value="strength">Strength</TabsTrigger>
                  <TabsTrigger value="valuation">Valuation</TabsTrigger>
                  <TabsTrigger value="news">News</TabsTrigger>
                </TabsList>

                <TabsContent value="price">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex gap-2">
                        {periods.map((p) => (
                          <Button
                            key={p}
                            variant={period === p ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setPeriod(p)}
                          >
                            {p}
                          </Button>
                        ))}
                      </div>
                      <div className={cn('text-lg font-semibold', getChangeColor(priceChange))}>
                        {priceChange > 0 ? '+' : ''}
                        {priceChange.toFixed(2)}%
                      </div>
                    </div>
                    {isLoadingPrice ? (
                      <Skeleton className="h-80 w-full" />
                    ) : priceData?.length ? (
                      <PriceChart data={priceData} height={350} />
                    ) : (
                      <p className="text-muted-foreground text-center py-12">
                        No price data available
                      </p>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="quality">
                  <div className="max-w-md">
                    <MetricRow label="ROIC" value={metrics?.quality?.roic} />
                    <MetricRow label="ROE" value={metrics?.quality?.roe} />
                    <MetricRow label="ROA" value={metrics?.quality?.roa} />
                    <MetricRow label="Gross Margin" value={metrics?.quality?.gross_margin} />
                    <MetricRow label="Operating Margin" value={metrics?.quality?.operating_margin} />
                    <MetricRow label="Net Margin" value={metrics?.quality?.net_margin} />
                    <MetricRow label="FCF Margin" value={metrics?.quality?.fcf_margin} />
                    <MetricRow label="Asset Turnover" value={metrics?.quality?.asset_turnover} format="ratio" />
                  </div>
                </TabsContent>

                <TabsContent value="growth">
                  <div className="max-w-md">
                    <MetricRow label="Revenue Growth 1Y" value={metrics?.growth?.revenue_growth_1y} />
                    <MetricRow label="Revenue CAGR 3Y" value={metrics?.growth?.revenue_cagr_3y} />
                    <MetricRow label="Revenue CAGR 5Y" value={metrics?.growth?.revenue_cagr_5y} />
                    <MetricRow label="Earnings Growth 1Y" value={metrics?.growth?.earnings_growth_1y} />
                    <MetricRow label="Earnings CAGR 3Y" value={metrics?.growth?.earnings_cagr_3y} />
                    <MetricRow label="FCF Growth 1Y" value={metrics?.growth?.fcf_growth_1y} />
                    <MetricRow label="FCF CAGR 3Y" value={metrics?.growth?.fcf_cagr_3y} />
                  </div>
                </TabsContent>

                <TabsContent value="strength">
                  <div className="max-w-md">
                    <MetricRow label="Current Ratio" value={metrics?.strength?.current_ratio} format="ratio" />
                    <MetricRow label="Quick Ratio" value={metrics?.strength?.quick_ratio} format="ratio" />
                    <MetricRow label="Debt/Equity" value={metrics?.strength?.debt_to_equity} format="ratio" inverse />
                    <MetricRow label="Interest Coverage" value={metrics?.strength?.interest_coverage} format="ratio" />
                  </div>
                </TabsContent>

                <TabsContent value="valuation">
                  <div className="max-w-md">
                    <MetricRow label="P/E Ratio" value={metrics?.valuation?.pe_ratio} format="ratio" inverse />
                    <MetricRow label="P/S Ratio" value={metrics?.valuation?.ps_ratio} format="ratio" inverse />
                    <MetricRow label="P/B Ratio" value={metrics?.valuation?.pb_ratio} format="ratio" inverse />
                    <MetricRow label="EV/EBITDA" value={metrics?.valuation?.ev_ebitda} format="ratio" inverse />
                    <MetricRow label="EV/Sales" value={metrics?.valuation?.ev_sales} format="ratio" inverse />
                    <MetricRow label="FCF Yield" value={metrics?.valuation?.fcf_yield} />
                    <MetricRow label="Earnings Yield" value={metrics?.valuation?.earnings_yield} />
                    <MetricRow label="PEG Ratio" value={metrics?.valuation?.peg_ratio} format="ratio" inverse />
                  </div>
                </TabsContent>

                <TabsContent value="news">
                  <div className="space-y-4">
                    {news?.length ? (
                      news.map((article, i) => (
                        <a
                          key={i}
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block p-4 rounded-lg border hover:bg-accent transition-colors"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <h4 className="font-medium mb-1">{article.title}</h4>
                              <p className="text-sm text-muted-foreground">
                                {article.publisher} •{' '}
                                {new Date(article.published_at).toLocaleDateString()}
                              </p>
                            </div>
                            <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                          </div>
                        </a>
                      ))
                    ) : (
                      <p className="text-muted-foreground text-center py-12">
                        No news available
                      </p>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Financial Trends */}
          {financials?.income_statements?.length && (
            <Card>
              <CardHeader>
                <CardTitle>Financial Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <FinancialChart data={financials.income_statements} height={300} />
              </CardContent>
            </Card>
          )}

          {/* Stage Classification */}
          {metrics?.stage && (
            <Card>
              <CardHeader>
                <button
                  onClick={() => setShowReasons(!showReasons)}
                  className="flex items-center justify-between w-full text-left"
                >
                  <CardTitle className="text-base">Stage Classification</CardTitle>
                  {showReasons ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </button>
              </CardHeader>
              {showReasons && (
                <CardContent>
                  <div className="flex items-center gap-2 mb-3">
                    <Badge
                      variant="outline"
                      className={cn('capitalize', getStageColor(metrics.stage.stage))}
                    >
                      {metrics.stage.stage}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      Confidence: {formatPercent(metrics.stage.confidence)}
                    </span>
                  </div>
                  <ul className="space-y-1">
                    {metrics.stage.reasons.map((reason, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-primary">•</span>
                        {reason}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              )}
            </Card>
          )}
        </>
      )}
    </div>
  )
}
