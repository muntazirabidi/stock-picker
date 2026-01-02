import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { useUniverseTickers, useScoreUniverseWithValuation, useValueScores } from '@/hooks/useUniverse'
import { cn, getStageColor, getScoreColor } from '@/lib/utils'
import type { UniverseType, CompanyScoreWithValuation } from '@/types'
import { RefreshCw, Search, TrendingUp, Target, DollarSign, Gem, Info } from 'lucide-react'
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts'

const universeOptions = [
  { value: 'sp500', label: 'S&P 500' },
  { value: 'nasdaq100', label: 'Nasdaq 100' },
  { value: 'midcap', label: 'S&P 400 MidCap' },
  { value: 'smallcap', label: 'S&P 600 SmallCap' },
]

const sortOptions = [
  { value: 'value_score', label: 'Value Score' },
  { value: 'quality_score', label: 'Quality' },
  { value: 'valuation_score', label: 'Valuation' },
  { value: 'fcf_yield', label: 'FCF Yield' },
  { value: 'pe_ratio', label: 'P/E Ratio' },
]

function formatMetric(value: number | null, suffix = '', decimals = 1): string {
  if (value === null || value === undefined) return '—'
  return `${value.toFixed(decimals)}${suffix}`
}

function formatPercent(value: number | null): string {
  if (value === null || value === undefined) return '—'
  return `${(value * 100).toFixed(1)}%`
}

function getValueColor(qualityScore: number, valuationScore: number): string {
  // High quality + high valuation score (cheap) = green (best value)
  // High quality + low valuation (expensive) = blue (quality but pricey)
  // Low quality + high valuation (cheap) = amber (value trap risk)
  // Low quality + low valuation = red (avoid)
  if (qualityScore >= 60 && valuationScore >= 60) return '#10b981' // emerald - best value
  if (qualityScore >= 60 && valuationScore < 60) return '#3b82f6' // blue - quality but expensive
  if (qualityScore < 60 && valuationScore >= 60) return '#f59e0b' // amber - value trap
  return '#ef4444' // red - avoid
}

export default function ValuePicks() {
  const navigate = useNavigate()
  const [universeType, setUniverseType] = useState<UniverseType>('sp500')
  const [sortBy, setSortBy] = useState('value_score')
  const [scoreCount, setScoreCount] = useState(50)
  const [searchTerm, setSearchTerm] = useState('')

  // Use global cache for scores (persists across navigation)
  const { data: scores, setData: setScores } = useValueScores()

  // Valuation filters
  const [maxPE, setMaxPE] = useState<number | ''>('')
  const [minFCFYield, setMinFCFYield] = useState<number | ''>('')
  const [minQuality, setMinQuality] = useState(50)

  const { data: tickers, isLoading: isLoadingTickers } = useUniverseTickers(universeType)
  const scoreMutation = useScoreUniverseWithValuation()

  const handleScore = async () => {
    if (!tickers?.length) return
    const tickersToScore = tickers.slice(0, scoreCount)
    const result = await scoreMutation.mutateAsync(tickersToScore)
    setScores(result)
  }

  const filteredAndSortedScores = useMemo(() => {
    let result = [...scores]

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(
        (s) =>
          s.ticker.toLowerCase().includes(term) ||
          s.name.toLowerCase().includes(term)
      )
    }

    // Filter by minimum quality
    result = result.filter((s) => s.quality_score >= minQuality)

    // Filter by max P/E
    if (maxPE !== '' && maxPE > 0) {
      result = result.filter((s) => s.pe_ratio === null || s.pe_ratio <= maxPE)
    }

    // Filter by min FCF Yield
    if (minFCFYield !== '' && minFCFYield > 0) {
      result = result.filter((s) => s.fcf_yield !== null && s.fcf_yield >= minFCFYield / 100)
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'value_score':
          return (b.value_score || 0) - (a.value_score || 0)
        case 'quality_score':
          return b.quality_score - a.quality_score
        case 'valuation_score':
          return b.valuation_score - a.valuation_score
        case 'fcf_yield':
          return (b.fcf_yield || 0) - (a.fcf_yield || 0)
        case 'pe_ratio':
          // Lower P/E is better, handle nulls
          if (a.pe_ratio === null) return 1
          if (b.pe_ratio === null) return -1
          return a.pe_ratio - b.pe_ratio
        default:
          return 0
      }
    })

    return result
  }, [scores, sortBy, searchTerm, minQuality, maxPE, minFCFYield])

  // Scatter chart data
  const scatterData = useMemo(() => {
    return filteredAndSortedScores.map((s) => ({
      ticker: s.ticker,
      name: s.name,
      quality: s.quality_score,
      valuation: s.valuation_score,
      value_score: s.value_score,
      pe_ratio: s.pe_ratio,
      fcf_yield: s.fcf_yield,
    }))
  }, [filteredAndSortedScores])

  // Stats
  const stats = useMemo(() => {
    if (!filteredAndSortedScores.length) return null
    const valuePicks = filteredAndSortedScores.filter(
      (s) => s.quality_score >= 60 && s.valuation_score >= 60
    )
    return {
      total: filteredAndSortedScores.length,
      valuePicks: valuePicks.length,
      avgValueScore: filteredAndSortedScores.reduce((sum, s) => sum + (s.value_score || 0), 0) / filteredAndSortedScores.length,
      topValueScore: Math.max(...filteredAndSortedScores.map((s) => s.value_score || 0)),
    }
  }, [filteredAndSortedScores])

  const maxTickers = tickers?.length || 500

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Gem className="h-8 w-8 text-emerald-400" />
            Value Picks
          </h1>
          <p className="text-muted-foreground">Find undervalued stocks with strong fundamentals</p>
        </div>
      </div>

      {/* Controls */}
      <Card className="bg-card/50 backdrop-blur border-border/50">
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4 items-end">
            <div className="space-y-2">
              <label className="text-sm font-medium">Universe</label>
              <Select
                value={universeType}
                onChange={(e) => setUniverseType(e.target.value as UniverseType)}
                options={universeOptions}
                className="w-40"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Analyze
                <span className="text-xs text-muted-foreground ml-1">
                  (of {isLoadingTickers ? '...' : maxTickers})
                </span>
              </label>
              <Input
                type="number"
                value={scoreCount}
                onChange={(e) => setScoreCount(Math.min(Math.max(1, Number(e.target.value)), maxTickers))}
                min={1}
                max={maxTickers}
                className="w-20"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Min Quality</label>
              <Input
                type="number"
                value={minQuality}
                onChange={(e) => setMinQuality(Number(e.target.value))}
                min={0}
                max={100}
                className="w-20"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Max P/E</label>
              <Input
                type="number"
                value={maxPE}
                onChange={(e) => setMaxPE(e.target.value ? Number(e.target.value) : '')}
                placeholder="Any"
                className="w-20"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Min FCF Yield %</label>
              <Input
                type="number"
                value={minFCFYield}
                onChange={(e) => setMinFCFYield(e.target.value ? Number(e.target.value) : '')}
                placeholder="Any"
                className="w-20"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Sort By</label>
              <Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                options={sortOptions}
                className="w-32"
              />
            </div>

            <div className="space-y-2 flex-1 min-w-48">
              <label className="text-sm font-medium">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search ticker or name..."
                  className="pl-9"
                />
              </div>
            </div>

            <Button
              onClick={handleScore}
              disabled={isLoadingTickers || scoreMutation.isPending}
              className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500"
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', scoreMutation.isPending && 'animate-spin')} />
              {scoreMutation.isPending ? 'Analyzing...' : 'Find Value'}
            </Button>
          </div>

          {/* Info banner */}
          <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground bg-emerald-500/10 rounded-lg px-4 py-2">
            <Info className="h-4 w-4 text-emerald-400" />
            <span>
              <strong>Value Score</strong> = (Quality + Valuation) / 2.
              Green zone = Quality ≥60 AND Valuation ≥60 (undervalued quality stocks).
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Target className="h-4 w-4" />
                Analyzed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-emerald-400 flex items-center gap-2">
                <Gem className="h-4 w-4" />
                Value Picks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400">{stats.valuePicks}</div>
              <p className="text-xs text-muted-foreground">Quality ≥60 & Value ≥60</p>
            </CardContent>
          </Card>
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Avg Value Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.avgValueScore.toFixed(1)}</div>
            </CardContent>
          </Card>
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Top Value Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400">{stats.topValueScore.toFixed(1)}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Quality vs Valuation Scatter Chart */}
      {scores.length > 0 && (
        <Card className="bg-card/50 backdrop-blur border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Quality vs Valuation Matrix
              <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">
                Sweet Spot: Top Right
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    type="number"
                    dataKey="quality"
                    name="Quality Score"
                    domain={[0, 100]}
                    label={{ value: 'Quality Score →', position: 'bottom', offset: 40, fill: '#94a3b8' }}
                    tick={{ fill: '#94a3b8' }}
                  />
                  <YAxis
                    type="number"
                    dataKey="valuation"
                    name="Valuation Score"
                    domain={[0, 100]}
                    label={{ value: '← Valuation Score (Higher = Cheaper)', angle: -90, position: 'left', offset: 40, fill: '#94a3b8' }}
                    tick={{ fill: '#94a3b8' }}
                  />
                  <ReferenceLine x={60} stroke="#475569" strokeDasharray="5 5" />
                  <ReferenceLine y={60} stroke="#475569" strokeDasharray="5 5" />
                  <Tooltip
                    content={({ payload }) => {
                      if (!payload?.[0]) return null
                      const data = payload[0].payload
                      return (
                        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
                          <p className="font-bold text-white">{data.ticker}</p>
                          <p className="text-sm text-slate-300">{data.name}</p>
                          <div className="mt-2 space-y-1 text-sm">
                            <p>Quality: <span className="text-blue-400">{data.quality.toFixed(0)}</span></p>
                            <p>Valuation: <span className="text-emerald-400">{data.valuation.toFixed(0)}</span></p>
                            <p>Value Score: <span className="text-amber-400">{data.value_score?.toFixed(0) || '—'}</span></p>
                            {data.pe_ratio && <p>P/E: {data.pe_ratio.toFixed(1)}</p>}
                            {data.fcf_yield && <p>FCF Yield: {(data.fcf_yield * 100).toFixed(1)}%</p>}
                          </div>
                        </div>
                      )
                    }}
                  />
                  <Scatter
                    data={scatterData}
                    cursor="pointer"
                    onClick={(data) => navigate(`/company/${data.ticker}`)}
                  >
                    {scatterData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={getValueColor(entry.quality, entry.valuation)}
                        fillOpacity={0.8}
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-muted-foreground">Value Pick (Q≥60, V≥60)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-muted-foreground">Quality but Expensive</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="text-muted-foreground">Value Trap Risk</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-muted-foreground">Avoid</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Table */}
      <Card className="bg-card/50 backdrop-blur border-border/50">
        <CardHeader>
          <CardTitle>Value Picks ({filteredAndSortedScores.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {scoreMutation.isPending ? (
            <div className="space-y-3">
              {[...Array(10)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : scores.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Gem className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">Click "Find Value" to discover undervalued quality stocks</p>
            </div>
          ) : (
            <div className="max-h-[600px] overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead>Ticker</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Stage</TableHead>
                    <TableHead>Value Score</TableHead>
                    <TableHead>Quality</TableHead>
                    <TableHead>Valuation</TableHead>
                    <TableHead>P/E</TableHead>
                    <TableHead>PEG</TableHead>
                    <TableHead>FCF Yield</TableHead>
                    <TableHead>EV/EBITDA</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAndSortedScores.map((score) => {
                    const isValuePick = score.quality_score >= 60 && score.valuation_score >= 60
                    return (
                      <TableRow
                        key={score.ticker}
                        className={cn(
                          'cursor-pointer transition-colors',
                          isValuePick && 'bg-emerald-500/5 hover:bg-emerald-500/10'
                        )}
                        onClick={() => navigate(`/company/${score.ticker}`)}
                      >
                        <TableCell className="font-semibold">
                          <div className="flex items-center gap-2">
                            {score.ticker}
                            {isValuePick && <Gem className="h-4 w-4 text-emerald-400" />}
                          </div>
                        </TableCell>
                        <TableCell className="max-w-40 truncate text-muted-foreground">
                          {score.name}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={cn('capitalize', getStageColor(score.stage))}
                          >
                            {score.stage}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <span className={cn('font-bold text-lg', getScoreColor(score.value_score || 0))}>
                              {score.value_score?.toFixed(0) || '—'}
                            </span>
                            <Progress
                              value={score.value_score || 0}
                              className="w-16 h-2"
                            />
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className={cn('font-medium', getScoreColor(score.quality_score))}>
                            {score.quality_score.toFixed(0)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className={cn('font-medium', getScoreColor(score.valuation_score))}>
                            {score.valuation_score.toFixed(0)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className={cn(
                            score.pe_ratio !== null && score.pe_ratio < 20 ? 'text-emerald-400' :
                            score.pe_ratio !== null && score.pe_ratio < 30 ? 'text-blue-400' :
                            score.pe_ratio !== null ? 'text-amber-400' : ''
                          )}>
                            {formatMetric(score.pe_ratio)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className={cn(
                            score.peg_ratio !== null && score.peg_ratio < 1 ? 'text-emerald-400' :
                            score.peg_ratio !== null && score.peg_ratio < 2 ? 'text-blue-400' :
                            score.peg_ratio !== null ? 'text-amber-400' : ''
                          )}>
                            {formatMetric(score.peg_ratio)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className={cn(
                            score.fcf_yield !== null && score.fcf_yield > 0.05 ? 'text-emerald-400' :
                            score.fcf_yield !== null && score.fcf_yield > 0.02 ? 'text-blue-400' :
                            score.fcf_yield !== null ? 'text-amber-400' : ''
                          )}>
                            {formatPercent(score.fcf_yield)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className={cn(
                            score.ev_ebitda !== null && score.ev_ebitda < 10 ? 'text-emerald-400' :
                            score.ev_ebitda !== null && score.ev_ebitda < 15 ? 'text-blue-400' :
                            score.ev_ebitda !== null ? 'text-amber-400' : ''
                          )}>
                            {formatMetric(score.ev_ebitda)}
                          </span>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
