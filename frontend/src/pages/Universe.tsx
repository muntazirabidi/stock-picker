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
import { useUniverseTickers, useScoreUniverse } from '@/hooks/useUniverse'
import { cn, getStageColor, getScoreColor } from '@/lib/utils'
import type { UniverseType, CompanyScore } from '@/types'
import { Download, RefreshCw, Search, Info, Zap, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'

const universeOptions = [
  { value: 'sp500', label: 'S&P 500 (503)' },
  { value: 'nasdaq100', label: 'Nasdaq 100 (101)' },
  { value: 'midcap', label: 'S&P 400 MidCap' },
  { value: 'smallcap', label: 'S&P 600 SmallCap' },
  { value: 'all', label: 'All S&P' },
]

const stageOptions = [
  { value: 'all', label: 'All Stages' },
  { value: 'compounder', label: 'Compounder' },
  { value: 'growth', label: 'Growth' },
  { value: 'mature', label: 'Mature' },
  { value: 'speculative', label: 'Speculative' },
]

const sortOptions = [
  { value: 'score', label: 'Score' },
  { value: 'quality', label: 'Quality' },
  { value: 'growth', label: 'Growth' },
  { value: 'strength', label: 'Strength' },
  { value: 'value', label: 'Value' },
  { value: 'ticker', label: 'Ticker' },
]

type SortKey = 'ticker' | 'name' | 'stage' | 'score' | 'quality' | 'growth' | 'strength' | 'value'
type SortDirection = 'asc' | 'desc'

export default function Universe() {
  const navigate = useNavigate()
  const [universeType, setUniverseType] = useState<UniverseType>('sp500')
  const [stageFilter, setStageFilter] = useState('all')
  const [sortBy, setSortBy] = useState<SortKey>('score')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [scoreCount, setScoreCount] = useState(20) // Default to 20 stocks
  const [minScore, setMinScore] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const [scores, setScores] = useState<CompanyScore[]>([])

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      // Toggle direction if same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      // New column, default to desc for scores, asc for text
      setSortBy(key)
      setSortDirection(key === 'ticker' || key === 'name' ? 'asc' : 'desc')
    }
  }

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortBy !== column) return <ArrowUpDown className="h-4 w-4 opacity-50" />
    return sortDirection === 'asc'
      ? <ArrowUp className="h-4 w-4 text-primary" />
      : <ArrowDown className="h-4 w-4 text-primary" />
  }

  const { data: tickers, isLoading: isLoadingTickers } = useUniverseTickers(universeType)
  const scoreMutation = useScoreUniverse()

  const handleScore = async () => {
    if (!tickers?.length) return
    // Only score the first N tickers
    const tickersToScore = tickers.slice(0, scoreCount)
    const result = await scoreMutation.mutateAsync(tickersToScore)
    setScores(result)
  }

  const filteredAndSortedScores = useMemo(() => {
    let result = [...scores]

    // Filter by stage
    if (stageFilter !== 'all') {
      result = result.filter((s) => s.stage === stageFilter)
    }

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(
        (s) =>
          s.ticker.toLowerCase().includes(term) ||
          s.name.toLowerCase().includes(term)
      )
    }

    // Filter by min score
    result = result.filter((s) => s.composite_score >= minScore)

    // Sort
    result.sort((a, b) => {
      let comparison = 0
      switch (sortBy) {
        case 'score':
          comparison = a.composite_score - b.composite_score
          break
        case 'quality':
          comparison = a.quality_score - b.quality_score
          break
        case 'growth':
          comparison = a.growth_score - b.growth_score
          break
        case 'strength':
          comparison = a.strength_score - b.strength_score
          break
        case 'value':
          comparison = a.valuation_score - b.valuation_score
          break
        case 'ticker':
          comparison = a.ticker.localeCompare(b.ticker)
          break
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'stage':
          comparison = a.stage.localeCompare(b.stage)
          break
        default:
          comparison = 0
      }
      return sortDirection === 'asc' ? comparison : -comparison
    })

    return result
  }, [scores, stageFilter, sortBy, sortDirection, minScore, searchTerm])

  const stats = useMemo(() => {
    if (!scores.length) return null
    return {
      total: scores.length,
      avgScore: scores.reduce((sum, s) => sum + s.composite_score, 0) / scores.length,
      topScore: Math.max(...scores.map((s) => s.composite_score)),
      compounders: scores.filter((s) => s.stage === 'compounder').length,
    }
  }, [scores])

  const handleExportCSV = () => {
    const headers = ['Ticker', 'Name', 'Stage', 'Score', 'Quality', 'Growth', 'Strength', 'Value']
    const rows = filteredAndSortedScores.map((s) => [
      s.ticker,
      s.name,
      s.stage,
      s.composite_score.toFixed(1),
      s.quality_score.toFixed(1),
      s.growth_score.toFixed(1),
      s.strength_score.toFixed(1),
      s.valuation_score.toFixed(1),
    ])

    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `universe_scores_${universeType}.csv`
    a.click()
  }

  const maxTickers = tickers?.length || 500

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Universe</h1>
          <p className="text-muted-foreground">Score and rank stocks</p>
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
                className="w-44"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                Score First
                <span className="text-xs text-muted-foreground">
                  (of {isLoadingTickers ? '...' : maxTickers})
                </span>
              </label>
              <Input
                type="number"
                value={scoreCount}
                onChange={(e) => setScoreCount(Math.min(Math.max(1, Number(e.target.value)), maxTickers))}
                min={1}
                max={maxTickers}
                className="w-24"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Stage</label>
              <Select
                value={stageFilter}
                onChange={(e) => setStageFilter(e.target.value)}
                options={stageOptions}
                className="w-36"
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

            <div className="space-y-2">
              <label className="text-sm font-medium">Min Score</label>
              <Input
                type="number"
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                min={0}
                max={100}
                className="w-20"
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
              className="bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90"
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', scoreMutation.isPending && 'animate-spin')} />
              {scoreMutation.isPending ? `Scoring ${scoreCount}...` : `Score ${scoreCount} Stocks`}
            </Button>
          </div>

          {/* Info banner */}
          <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground bg-accent/50 rounded-lg px-4 py-2">
            <Info className="h-4 w-4 text-primary" />
            <span>
              Data is cached for 24 hours. First run fetches from API (~3-5s per stock).
              Subsequent runs use cache and are instant.
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Scored
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Average Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.avgScore.toFixed(1)}</div>
            </CardContent>
          </Card>
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Top Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400">{stats.topScore.toFixed(1)}</div>
            </CardContent>
          </Card>
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Compounders
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400">{stats.compounders}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Results Table */}
      <Card className="bg-card/50 backdrop-blur border-border/50">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Results ({filteredAndSortedScores.length})</CardTitle>
          {scores.length > 0 && (
            <Button variant="outline" size="sm" onClick={handleExportCSV}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {scoreMutation.isPending ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <Zap className="h-4 w-4 text-primary animate-pulse" />
                <span>Fetching and scoring {scoreCount} stocks... This may take a few minutes on first run.</span>
              </div>
              {[...Array(10)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : scores.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p className="text-lg mb-2">Select a universe and click "Score" to begin</p>
              <p className="text-sm">
                {isLoadingTickers
                  ? 'Loading tickers...'
                  : tickers
                  ? `${tickers.length} tickers available`
                  : ''}
              </p>
            </div>
          ) : (
            <div className="max-h-[600px] overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('ticker')}
                    >
                      <div className="flex items-center gap-1">
                        Ticker <SortIcon column="ticker" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('name')}
                    >
                      <div className="flex items-center gap-1">
                        Name <SortIcon column="name" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('stage')}
                    >
                      <div className="flex items-center gap-1">
                        Stage <SortIcon column="stage" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('score')}
                    >
                      <div className="flex items-center gap-1">
                        Score <SortIcon column="score" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('quality')}
                    >
                      <div className="flex items-center gap-1">
                        Quality <SortIcon column="quality" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('growth')}
                    >
                      <div className="flex items-center gap-1">
                        Growth <SortIcon column="growth" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('strength')}
                    >
                      <div className="flex items-center gap-1">
                        Strength <SortIcon column="strength" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer hover:text-primary transition-colors select-none"
                      onClick={() => handleSort('value')}
                    >
                      <div className="flex items-center gap-1">
                        Value <SortIcon column="value" />
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAndSortedScores.map((score) => (
                    <TableRow
                      key={score.ticker}
                      className="cursor-pointer transition-colors"
                      onClick={() => navigate(`/company/${score.ticker}`)}
                    >
                      <TableCell className="font-semibold">{score.ticker}</TableCell>
                      <TableCell className="max-w-48 truncate text-muted-foreground">{score.name}</TableCell>
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
                          <span className={cn('font-bold text-lg', getScoreColor(score.composite_score))}>
                            {score.composite_score.toFixed(0)}
                          </span>
                          <Progress
                            value={score.composite_score}
                            className="w-20 h-2"
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{score.quality_score.toFixed(0)}</span>
                          <Progress value={score.quality_score} className="w-12 h-1.5" />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{score.growth_score.toFixed(0)}</span>
                          <Progress value={score.growth_score} className="w-12 h-1.5" />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{score.strength_score.toFixed(0)}</span>
                          <Progress value={score.strength_score} className="w-12 h-1.5" />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{score.valuation_score.toFixed(0)}</span>
                          <Progress value={score.valuation_score} className="w-12 h-1.5" />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
