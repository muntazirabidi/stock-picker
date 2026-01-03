import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
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
import { RefreshCw, Search, TrendingUp, Target, DollarSign, Gem, Info, ChevronUp, ChevronDown } from 'lucide-react'
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
  { value: 'growth_score', label: 'Growth' },
  { value: 'valuation_score', label: 'Valuation' },
  { value: 'fcf_yield', label: 'FCF Yield' },
  { value: 'pe_ratio', label: 'P/E Ratio' },
  { value: 'peg_ratio', label: 'PEG Ratio' },
]

function formatMetric(value: number | null, suffix = '', decimals = 1): string {
  if (value === null || value === undefined) return '—'
  return `${value.toFixed(decimals)}${suffix}`
}

function formatPercent(value: number | null): string {
  if (value === null || value === undefined) return '—'
  return `${(value * 100).toFixed(1)}%`
}

type SortKey = 'ticker' | 'name' | 'stage' | 'value_score' | 'quality_score' | 'growth_score' | 'valuation_score' | 'pe_ratio' | 'peg_ratio' | 'fcf_yield' | 'ev_ebitda'
type SortDirection = 'asc' | 'desc'

function SortIcon({ column, sortBy, sortDirection }: { column: SortKey; sortBy: SortKey; sortDirection: SortDirection }) {
  if (sortBy !== column) return <ChevronUp className="h-4 w-4 opacity-20" />
  return sortDirection === 'asc'
    ? <ChevronUp className="h-4 w-4 text-primary" />
    : <ChevronDown className="h-4 w-4 text-primary" />
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
  const [sortBy, setSortBy] = useState<SortKey>('value_score')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [scoreCount, setScoreCount] = useState(500)
  const [searchTerm, setSearchTerm] = useState('')

  // Use global cache for scores (persists across navigation)
  const { data: scores, setData: setScores } = useValueScores()

  // Valuation filters
  const [minValueScore, setMinValueScore] = useState<number | ''>(80)
  const [maxPE, setMaxPE] = useState<number | ''>(25)
  const [maxPEG, setMaxPEG] = useState<number | ''>(1.5)
  const [minFCFYield, setMinFCFYield] = useState<number | ''>(5)
  const [minQuality, setMinQuality] = useState(60)
  const [minGrowthScore, setMinGrowthScore] = useState<number | ''>('')
  const [stageFilter, setStageFilter] = useState<string>('all')

  const { data: tickers, isLoading: isLoadingTickers } = useUniverseTickers(universeType)
  const scoreMutation = useScoreUniverseWithValuation()

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(key)
      // Default to desc for scores/metrics (higher is better), asc for P/E and PEG (lower is better)
      const defaultDesc = ['value_score', 'quality_score', 'growth_score', 'valuation_score', 'fcf_yield']
      setSortDirection(defaultDesc.includes(key) ? 'desc' : 'asc')
    }
  }

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

    // Filter by minimum value score
    if (minValueScore !== '' && minValueScore > 0) {
      result = result.filter((s) => (s.value_score || 0) >= minValueScore)
    }

    // Filter by max P/E
    if (maxPE !== '' && maxPE > 0) {
      result = result.filter((s) => s.pe_ratio === null || s.pe_ratio <= maxPE)
    }

    // Filter by max PEG
    if (maxPEG !== '' && maxPEG > 0) {
      result = result.filter((s) => s.peg_ratio === null || s.peg_ratio <= maxPEG)
    }

    // Filter by min FCF Yield
    if (minFCFYield !== '' && minFCFYield > 0) {
      result = result.filter((s) => s.fcf_yield !== null && s.fcf_yield >= minFCFYield / 100)
    }

    // Filter by min Growth Score
    if (minGrowthScore !== '' && minGrowthScore > 0) {
      result = result.filter((s) => s.growth_score >= minGrowthScore)
    }

    // Filter by stage
    if (stageFilter !== 'all') {
      result = result.filter((s) => s.stage === stageFilter)
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'ticker':
          comparison = a.ticker.localeCompare(b.ticker)
          break
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'stage':
          comparison = a.stage.localeCompare(b.stage)
          break
        case 'value_score':
          comparison = (a.value_score || 0) - (b.value_score || 0)
          break
        case 'quality_score':
          comparison = a.quality_score - b.quality_score
          break
        case 'growth_score':
          comparison = a.growth_score - b.growth_score
          break
        case 'valuation_score':
          comparison = a.valuation_score - b.valuation_score
          break
        case 'pe_ratio':
          // Handle nulls - push to end
          if (a.pe_ratio === null && b.pe_ratio === null) comparison = 0
          else if (a.pe_ratio === null) comparison = 1
          else if (b.pe_ratio === null) comparison = -1
          else comparison = a.pe_ratio - b.pe_ratio
          break
        case 'peg_ratio':
          // Handle nulls - push to end
          if (a.peg_ratio === null && b.peg_ratio === null) comparison = 0
          else if (a.peg_ratio === null) comparison = 1
          else if (b.peg_ratio === null) comparison = -1
          else comparison = a.peg_ratio - b.peg_ratio
          break
        case 'fcf_yield':
          comparison = (a.fcf_yield || 0) - (b.fcf_yield || 0)
          break
        case 'ev_ebitda':
          // Handle nulls - push to end
          if (a.ev_ebitda === null && b.ev_ebitda === null) comparison = 0
          else if (a.ev_ebitda === null) comparison = 1
          else if (b.ev_ebitda === null) comparison = -1
          else comparison = a.ev_ebitda - b.ev_ebitda
          break
        default:
          comparison = 0
      }

      return sortDirection === 'asc' ? comparison : -comparison
    })

    return result
  }, [scores, sortBy, sortDirection, searchTerm, minQuality, minValueScore, maxPE, maxPEG, minFCFYield, minGrowthScore, stageFilter])

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
      {/* Header */}
      <div className="relative overflow-hidden rounded-2xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0f0f14] p-6">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(16,185,129,0.08),transparent_60%)]" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[1px] bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent" />
        <div className="relative flex items-center gap-4">
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <Gem className="h-6 w-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Value Picks</h1>
            <p className="text-sm text-zinc-400">Find undervalued stocks with strong fundamentals</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] p-6">
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
              <label className="text-sm font-medium text-emerald-400">Min Value Score</label>
              <Input
                type="number"
                value={minValueScore}
                onChange={(e) => setMinValueScore(e.target.value ? Number(e.target.value) : '')}
                placeholder="Any"
                min={0}
                max={100}
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
              <label className="text-sm font-medium text-emerald-400">Max PEG</label>
              <Input
                type="number"
                value={maxPEG}
                onChange={(e) => setMaxPEG(e.target.value ? Number(e.target.value) : '')}
                placeholder="Any"
                step="0.1"
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
              <label className="text-sm font-medium text-blue-400">Min Growth Score</label>
              <Input
                type="number"
                value={minGrowthScore}
                onChange={(e) => setMinGrowthScore(e.target.value ? Number(e.target.value) : '')}
                placeholder="Any"
                min={0}
                max={100}
                className="w-20"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-blue-400">Stage</label>
              <Select
                value={stageFilter}
                onChange={(e) => setStageFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Stages' },
                  { value: 'compounder', label: 'Compounder' },
                  { value: 'mature', label: 'Mature' },
                  { value: 'growth', label: 'Growth' },
                ]}
                className="w-32"
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

          {/* Filter presets */}
          <div className="mt-5 pt-5 border-t border-white/[0.04] flex flex-wrap items-center gap-3">
            <span className="text-[12px] text-zinc-500 font-medium">Quick filters:</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setMinValueScore(80)
                setMinQuality(60)
                setMaxPE(25)
                setMaxPEG(1.5)
                setMinFCFYield(5)
                setMinGrowthScore('')
                setStageFilter('all')
              }}
              className="border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/50 text-[12px]"
            >
              <Gem className="h-3 w-3 mr-1.5" />
              Value Picks
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setMinValueScore('')
                setMinQuality(80)
                setMaxPE('')
                setMaxPEG(2.0)
                setMinFCFYield('')
                setMinGrowthScore(70)
                setStageFilter('compounder')
              }}
              className="border-blue-500/30 text-blue-400 hover:bg-blue-500/10 hover:border-blue-500/50 text-[12px]"
            >
              <TrendingUp className="h-3 w-3 mr-1.5" />
              Growth Picks
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setMinValueScore('')
                setMinQuality(0)
                setMaxPE('')
                setMaxPEG('')
                setMinFCFYield('')
                setMinGrowthScore('')
                setStageFilter('all')
              }}
              className="border-white/[0.06] text-zinc-400 hover:bg-white/[0.04] hover:border-white/[0.1] text-[12px]"
            >
              Reset All
            </Button>
          </div>
          <div className="mt-3 text-[11px] text-zinc-500 space-y-0.5">
            <p><span className="text-emerald-400/80">Value Picks:</span> Value≥80, Quality≥60, P/E≤25, PEG≤1.5, FCF≥5%</p>
            <p><span className="text-blue-400/80">Growth Picks:</span> Quality≥80, Growth≥70, PEG≤2.0, Stage=Compounder</p>
          </div>

          {/* Info banner */}
          <div className="mt-5 space-y-3">
            <div className="flex items-center gap-3 text-[12px] text-zinc-300 bg-emerald-500/[0.06] border border-emerald-500/10 rounded-lg px-4 py-3">
              <Info className="h-4 w-4 text-emerald-400 flex-shrink-0" />
              <span>
                <strong className="text-emerald-400">Value Score</strong> = (Quality + Valuation) / 2.
                Green zone = Quality ≥60 AND Valuation ≥60 (undervalued quality stocks).
              </span>
            </div>
            <details className="text-[12px] bg-white/[0.02] border border-white/[0.04] rounded-lg group">
              <summary className="px-4 py-3 cursor-pointer text-zinc-400 hover:text-zinc-200 transition-colors">
                Why these filter criteria? (click to expand)
              </summary>
              <div className="px-4 py-4 border-t border-white/[0.04] space-y-2 text-zinc-400">
                <p><strong className="text-emerald-400">Value Score ≥80:</strong> Top 20% combining quality + cheapness. Filters out mediocre stocks.</p>
                <p><strong className="text-blue-400">Quality ≥60:</strong> Above-average business fundamentals. Avoids struggling companies.</p>
                <p><strong className="text-purple-400">P/E ≤25:</strong> Not overpaying for earnings. Market average ~20.</p>
                <p><strong className="text-amber-400">PEG ≤1.5:</strong> Growth-adjusted P/E. Below 1.5 means growth isn't overpriced.</p>
                <p><strong className="text-teal-400">FCF Yield ≥5%:</strong> Real cash return. 5% = company generates 5¢ cash per $1 invested.</p>
                <p className="pt-2 text-amber-400/70 text-[11px]">
                  Note: Low PEG + Low Valuation Score = expensive but growing fast. Always check both!
                </p>
              </div>
            </details>
          </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] p-5">
            <div className="flex items-center gap-2 mb-3">
              <Target className="h-4 w-4 text-zinc-500" />
              <span className="text-[11px] text-zinc-500 uppercase tracking-wider font-medium">Analyzed</span>
            </div>
            <p className="text-3xl font-bold font-mono text-white">{stats.total}</p>
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/[0.08] to-teal-500/[0.04] p-5">
            <div className="flex items-center gap-2 mb-3">
              <Gem className="h-4 w-4 text-emerald-400" />
              <span className="text-[11px] text-emerald-400 uppercase tracking-wider font-medium">Value Picks</span>
            </div>
            <p className="text-3xl font-bold font-mono text-emerald-400">{stats.valuePicks}</p>
            <p className="text-[10px] text-zinc-500 mt-1">Quality ≥60 & Value ≥60</p>
          </div>
          <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] p-5">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-4 w-4 text-zinc-500" />
              <span className="text-[11px] text-zinc-500 uppercase tracking-wider font-medium">Avg Value</span>
            </div>
            <p className="text-3xl font-bold font-mono text-white">{stats.avgValueScore.toFixed(1)}</p>
          </div>
          <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] p-5">
            <div className="flex items-center gap-2 mb-3">
              <DollarSign className="h-4 w-4 text-zinc-500" />
              <span className="text-[11px] text-zinc-500 uppercase tracking-wider font-medium">Top Score</span>
            </div>
            <p className="text-3xl font-bold font-mono text-emerald-400">{stats.topValueScore.toFixed(1)}</p>
          </div>
        </div>
      )}

      {/* Quality vs Valuation Scatter Chart */}
      {scores.length > 0 && (
        <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] overflow-hidden">
          <div className="border-b border-white/[0.04] bg-white/[0.01] px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                  <Target className="h-5 w-5 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-[15px] font-semibold text-white">Quality vs Valuation Matrix</h3>
                  <p className="text-[12px] text-zinc-500 mt-0.5">Click any point to view company details</p>
                </div>
              </div>
              <span className="text-[11px] font-medium px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Sweet Spot: Top Right
              </span>
            </div>
          </div>
          <div className="p-0">
            <div className="h-[480px] relative">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 40, right: 40, bottom: 60, left: 80 }}>
                  <defs>
                    {/* Gradient backgrounds for quadrants */}
                    <linearGradient id="greenZone" x1="0" y1="1" x2="0" y2="0">
                      <stop offset="0%" stopColor="#10b981" stopOpacity="0.03" />
                      <stop offset="100%" stopColor="#10b981" stopOpacity="0.08" />
                    </linearGradient>
                    <linearGradient id="blueZone" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.02" />
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.05" />
                    </linearGradient>
                    <linearGradient id="amberZone" x1="0" y1="1" x2="0" y2="0">
                      <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.02" />
                      <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.05" />
                    </linearGradient>
                    <linearGradient id="redZone" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ef4444" stopOpacity="0.02" />
                      <stop offset="100%" stopColor="#ef4444" stopOpacity="0.04" />
                    </linearGradient>
                    {/* Glow filter for dots */}
                    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>

                  {/* Quadrant backgrounds */}
                  <rect x="60%" y="0" width="40%" height="40%" fill="url(#greenZone)" />
                  <rect x="0" y="0" width="60%" height="40%" fill="url(#amberZone)" />
                  <rect x="60%" y="40%" width="40%" height="60%" fill="url(#blueZone)" />
                  <rect x="0" y="40%" width="60%" height="60%" fill="url(#redZone)" />

                  <CartesianGrid
                    strokeDasharray="1 4"
                    stroke="#334155"
                    strokeOpacity={0.5}
                    vertical={true}
                    horizontal={true}
                  />

                  <XAxis
                    type="number"
                    dataKey="quality"
                    name="Quality Score"
                    domain={[0, 100]}
                    tickLine={false}
                    axisLine={{ stroke: '#475569', strokeWidth: 1 }}
                    tick={{ fill: '#71717a', fontSize: 11 }}
                    ticks={[0, 20, 40, 60, 80, 100]}
                    label={{
                      value: 'Quality Score →',
                      position: 'bottom',
                      offset: 10,
                      fill: '#94a3b8',
                      fontSize: 12,
                      fontWeight: 500,
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey="valuation"
                    name="Valuation Score"
                    domain={[0, 100]}
                    tickLine={false}
                    axisLine={{ stroke: '#475569', strokeWidth: 1 }}
                    tick={{ fill: '#71717a', fontSize: 11 }}
                    ticks={[0, 20, 40, 60, 80, 100]}
                    width={50}
                    label={{
                      value: 'Valuation Score (Higher = Cheaper)',
                      angle: -90,
                      position: 'insideLeft',
                      offset: 10,
                      fill: '#94a3b8',
                      fontSize: 12,
                      fontWeight: 500,
                      style: { textAnchor: 'middle' },
                    }}
                  />

                  {/* Threshold lines */}
                  <ReferenceLine
                    x={60}
                    stroke="#525252"
                    strokeWidth={1}
                    strokeDasharray="6 4"
                  />
                  <ReferenceLine
                    y={60}
                    stroke="#525252"
                    strokeWidth={1}
                    strokeDasharray="6 4"
                  />

                  <Tooltip
                    content={({ payload }) => {
                      if (!payload?.[0]) return null
                      const data = payload[0].payload
                      const isValuePick = data.quality >= 60 && data.valuation >= 60
                      return (
                        <div className="bg-slate-900/95 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 shadow-2xl min-w-[200px]">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-bold text-lg text-white">{data.ticker}</span>
                            {isValuePick && (
                              <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                VALUE PICK
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-slate-400 mb-3 line-clamp-1">{data.name}</p>
                          <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-0.5">
                              <p className="text-[10px] uppercase tracking-wider text-slate-500">Quality</p>
                              <p className="text-xl font-bold text-blue-400">{data.quality.toFixed(0)}</p>
                            </div>
                            <div className="space-y-0.5">
                              <p className="text-[10px] uppercase tracking-wider text-slate-500">Valuation</p>
                              <p className="text-xl font-bold text-emerald-400">{data.valuation.toFixed(0)}</p>
                            </div>
                          </div>
                          <div className="mt-3 pt-3 border-t border-slate-700/50 space-y-1.5">
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-500">Value Score</span>
                              <span className="font-semibold text-amber-400">{data.value_score?.toFixed(0) || '—'}</span>
                            </div>
                            {data.pe_ratio && (
                              <div className="flex justify-between text-sm">
                                <span className="text-slate-500">P/E Ratio</span>
                                <span className="font-medium">{data.pe_ratio.toFixed(1)}</span>
                              </div>
                            )}
                            {data.fcf_yield && (
                              <div className="flex justify-between text-sm">
                                <span className="text-slate-500">FCF Yield</span>
                                <span className="font-medium text-teal-400">{(data.fcf_yield * 100).toFixed(1)}%</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    }}
                    cursor={{ strokeDasharray: '3 3', stroke: '#6366f1' }}
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
                        fillOpacity={0.9}
                        stroke={getValueColor(entry.quality, entry.valuation)}
                        strokeWidth={2}
                        strokeOpacity={0.3}
                        r={7}
                        filter="url(#glow)"
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>

              {/* Quadrant labels */}
              <div className="absolute top-12 right-12 text-[10px] font-semibold text-emerald-400/60 uppercase tracking-widest pointer-events-none">
                Value Picks
              </div>
              <div className="absolute top-12 left-24 text-[10px] font-semibold text-amber-400/60 uppercase tracking-widest pointer-events-none">
                Value Traps
              </div>
              <div className="absolute bottom-24 right-12 text-[10px] font-semibold text-blue-400/60 uppercase tracking-widest pointer-events-none">
                Quality Premium
              </div>
              <div className="absolute bottom-24 left-24 text-[10px] font-semibold text-red-400/60 uppercase tracking-widest pointer-events-none">
                Avoid
              </div>
            </div>

            {/* Legend */}
            <div className="px-6 py-4 border-t border-white/[0.04] bg-white/[0.01]">
              <div className="flex flex-wrap justify-center gap-x-8 gap-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/30" />
                  <span className="text-[12px] text-zinc-400">Value Pick <span className="text-zinc-600">(Q≥60, V≥60)</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500 shadow-lg shadow-blue-500/30" />
                  <span className="text-[12px] text-zinc-400">Quality but Expensive</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-amber-500 shadow-lg shadow-amber-500/30" />
                  <span className="text-[12px] text-zinc-400">Value Trap Risk</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500 shadow-lg shadow-red-500/30" />
                  <span className="text-[12px] text-zinc-400">Avoid</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results Table */}
      <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] overflow-hidden">
        <div className="border-b border-white/[0.04] bg-white/[0.01] px-6 py-4">
          <h3 className="text-[15px] font-semibold text-white">Value Picks ({filteredAndSortedScores.length})</h3>
        </div>
        <div className="p-6">
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
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('ticker')}
                    >
                      <div className="flex items-center gap-1">
                        Ticker
                        <SortIcon column="ticker" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('name')}
                    >
                      <div className="flex items-center gap-1">
                        Name
                        <SortIcon column="name" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('stage')}
                    >
                      <div className="flex items-center gap-1">
                        Stage
                        <SortIcon column="stage" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('value_score')}
                    >
                      <div className="flex items-center gap-1">
                        Value Score
                        <SortIcon column="value_score" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('quality_score')}
                    >
                      <div className="flex items-center gap-1">
                        Quality
                        <SortIcon column="quality_score" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('growth_score')}
                    >
                      <div className="flex items-center gap-1">
                        Growth
                        <SortIcon column="growth_score" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('valuation_score')}
                    >
                      <div className="flex items-center gap-1">
                        Valuation
                        <SortIcon column="valuation_score" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('pe_ratio')}
                    >
                      <div className="flex items-center gap-1">
                        P/E
                        <SortIcon column="pe_ratio" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('peg_ratio')}
                    >
                      <div className="flex items-center gap-1">
                        PEG
                        <SortIcon column="peg_ratio" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('fcf_yield')}
                    >
                      <div className="flex items-center gap-1">
                        FCF Yield
                        <SortIcon column="fcf_yield" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('ev_ebitda')}
                    >
                      <div className="flex items-center gap-1">
                        EV/EBITDA
                        <SortIcon column="ev_ebitda" sortBy={sortBy} sortDirection={sortDirection} />
                      </div>
                    </TableHead>
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
                          <span className={cn('font-medium', getScoreColor(score.growth_score))}>
                            {score.growth_score.toFixed(0)}
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
        </div>
      </div>
    </div>
  )
}
