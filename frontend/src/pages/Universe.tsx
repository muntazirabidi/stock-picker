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
import { Download, RefreshCw, Search } from 'lucide-react'

const universeOptions = [
  { value: 'sp500', label: 'S&P 500' },
  { value: 'nasdaq100', label: 'Nasdaq 100' },
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

const topNOptions = [
  { value: '10', label: 'Top 10' },
  { value: '20', label: 'Top 20' },
  { value: '50', label: 'Top 50' },
  { value: '100', label: 'Top 100' },
  { value: 'all', label: 'All' },
]

export default function Universe() {
  const navigate = useNavigate()
  const [universeType, setUniverseType] = useState<UniverseType>('sp500')
  const [stageFilter, setStageFilter] = useState('all')
  const [sortBy, setSortBy] = useState('score')
  const [topN, setTopN] = useState('50')
  const [minScore, setMinScore] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const [scores, setScores] = useState<CompanyScore[]>([])

  const { data: tickers, isLoading: isLoadingTickers } = useUniverseTickers(universeType)
  const scoreMutation = useScoreUniverse()

  const handleScore = async () => {
    if (!tickers?.length) return
    const result = await scoreMutation.mutateAsync(tickers)
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
      switch (sortBy) {
        case 'score':
          return b.composite_score - a.composite_score
        case 'quality':
          return b.quality_score - a.quality_score
        case 'growth':
          return b.growth_score - a.growth_score
        case 'strength':
          return b.strength_score - a.strength_score
        case 'value':
          return b.valuation_score - a.valuation_score
        case 'ticker':
          return a.ticker.localeCompare(b.ticker)
        default:
          return 0
      }
    })

    // Limit results
    if (topN !== 'all') {
      result = result.slice(0, parseInt(topN))
    }

    return result
  }, [scores, stageFilter, sortBy, topN, minScore, searchTerm])

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-light tracking-tight">Universe</h1>
          <p className="text-muted-foreground">Score and rank stocks</p>
        </div>
      </div>

      {/* Controls */}
      <Card>
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
              <label className="text-sm font-medium">Show</label>
              <Select
                value={topN}
                onChange={(e) => setTopN(e.target.value)}
                options={topNOptions}
                className="w-28"
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
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', scoreMutation.isPending && 'animate-spin')} />
              {scoreMutation.isPending ? 'Scoring...' : 'Score Universe'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Scored
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Average Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avgScore.toFixed(1)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Top Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">{stats.topScore.toFixed(1)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Compounders
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">{stats.compounders}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Results Table */}
      <Card>
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
              {[...Array(10)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : scores.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>Select a universe and click "Score Universe" to begin</p>
              <p className="text-sm mt-1">
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
                  <TableRow>
                    <TableHead>Ticker</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Stage</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead>Quality</TableHead>
                    <TableHead>Growth</TableHead>
                    <TableHead>Strength</TableHead>
                    <TableHead>Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAndSortedScores.map((score) => (
                    <TableRow
                      key={score.ticker}
                      className="cursor-pointer"
                      onClick={() => navigate(`/company/${score.ticker}`)}
                    >
                      <TableCell className="font-medium">{score.ticker}</TableCell>
                      <TableCell className="max-w-48 truncate">{score.name}</TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={cn('capitalize', getStageColor(score.stage))}
                        >
                          {score.stage}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className={cn('font-semibold', getScoreColor(score.composite_score))}>
                            {score.composite_score.toFixed(0)}
                          </span>
                          <Progress
                            value={score.composite_score}
                            className="w-16 h-2"
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{score.quality_score.toFixed(0)}</span>
                          <Progress value={score.quality_score} className="w-12 h-1.5" />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{score.growth_score.toFixed(0)}</span>
                          <Progress value={score.growth_score} className="w-12 h-1.5" />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{score.strength_score.toFixed(0)}</span>
                          <Progress value={score.strength_score} className="w-12 h-1.5" />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{score.valuation_score.toFixed(0)}</span>
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
