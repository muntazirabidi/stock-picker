import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { AllocationChart } from '@/components/charts/AllocationChart'
import {
  usePortfolioHoldings,
  usePortfolioAllocation,
  useAddHolding,
  useDeployCapital,
} from '@/hooks/usePortfolio'
import {
  cn,
  formatCurrency,
  formatPercent,
  getChangeColor,
} from '@/lib/utils'
import type { Tier } from '@/types'
import { Plus, Wallet, TrendingUp, TrendingDown, AlertCircle, DollarSign } from 'lucide-react'

const tierOptions = [
  { value: 'tier_1', label: 'Tier 1 (Established)' },
  { value: 'tier_2', label: 'Tier 2 (Growth)' },
  { value: 'tier_3', label: 'Tier 3 (Opportunistic)' },
]

const tierLabels: Record<Tier, string> = {
  tier_1: 'Tier 1',
  tier_2: 'Tier 2',
  tier_3: 'Tier 3',
}

export default function Portfolio() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')

  // Form state for adding position
  const [newTicker, setNewTicker] = useState('')
  const [newShares, setNewShares] = useState('')
  const [newCost, setNewCost] = useState('')
  const [newDate, setNewDate] = useState('')
  const [newTier, setNewTier] = useState<Tier>('tier_1')
  const [newNotes, setNewNotes] = useState('')

  // Deploy state
  const [deployAmount, setDeployAmount] = useState('')

  usePortfolioHoldings() // Used to trigger refetch on mutation
  const { data: allocation, isLoading: isLoadingAllocation } = usePortfolioAllocation()
  const addHoldingMutation = useAddHolding()
  const deployMutation = useDeployCapital()

  const handleAddPosition = async () => {
    if (!newTicker || !newShares || !newCost || !newDate) return

    await addHoldingMutation.mutateAsync({
      ticker: newTicker.toUpperCase(),
      shares: parseFloat(newShares),
      cost_basis: parseFloat(newCost),
      purchase_date: newDate,
      tier: newTier,
      notes: newNotes || null,
    })

    // Reset form
    setNewTicker('')
    setNewShares('')
    setNewCost('')
    setNewDate('')
    setNewNotes('')
    setActiveTab('overview')
  }

  const handleDeploy = async () => {
    const amount = parseFloat(deployAmount)
    if (!amount || amount <= 0) return
    await deployMutation.mutateAsync(amount)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-light tracking-tight">Portfolio</h1>
        <p className="text-muted-foreground">Track holdings and allocations</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="add">Add Position</TabsTrigger>
          <TabsTrigger value="deploy">Deploy Capital</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          {isLoadingAllocation ? (
            <div className="grid gap-4 md:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : allocation ? (
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <Wallet className="h-4 w-4" />
                    <span className="text-sm">Total Value</span>
                  </div>
                  <p className="text-2xl font-bold">
                    {formatCurrency(allocation.total_value)}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    {allocation.total_gain_loss >= 0 ? (
                      <TrendingUp className="h-4 w-4 text-success" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-error" />
                    )}
                    <span className="text-sm">Gain/Loss</span>
                  </div>
                  <p className={cn('text-2xl font-bold', getChangeColor(allocation.total_gain_loss))}>
                    {allocation.total_gain_loss >= 0 ? '+' : ''}
                    {formatCurrency(allocation.total_gain_loss)}
                    <span className="text-base ml-1">
                      ({formatPercent(allocation.total_gain_loss_pct)})
                    </span>
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <span className="text-sm">Positions</span>
                  </div>
                  <p className="text-2xl font-bold">{allocation.positions.length}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-sm">Cost Basis</span>
                  </div>
                  <p className="text-2xl font-bold">{formatCurrency(allocation.total_cost)}</p>
                </CardContent>
              </Card>
            </div>
          ) : null}

          {/* Allocation */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Tier Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                {allocation?.tier_allocations && (
                  <AllocationChart data={allocation.tier_allocations} height={280} />
                )}
              </CardContent>
            </Card>

            {/* Target vs Actual */}
            <Card>
              <CardHeader>
                <CardTitle>Target vs Actual</CardTitle>
              </CardHeader>
              <CardContent>
                {allocation?.tier_allocations?.map((tier) => (
                  <div
                    key={tier.tier}
                    className="flex items-center justify-between py-3 border-b last:border-0"
                  >
                    <div>
                      <p className="font-medium">{tierLabels[tier.tier]}</p>
                      <p className="text-sm text-muted-foreground">
                        {tier.num_positions} positions
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">
                          Target: {formatPercent(tier.target_pct)}
                        </span>
                        <span
                          className={cn(
                            'font-medium',
                            tier.is_underweight
                              ? 'text-warning'
                              : tier.is_overweight
                              ? 'text-error'
                              : 'text-success'
                          )}
                        >
                          Actual: {formatPercent(tier.actual_pct)}
                        </span>
                      </div>
                      <p
                        className={cn(
                          'text-sm',
                          tier.is_underweight ? 'text-warning' : tier.is_overweight ? 'text-error' : ''
                        )}
                      >
                        {tier.is_underweight && (
                          <span className="flex items-center gap-1">
                            <AlertCircle className="h-3 w-3" />
                            Underweight by {formatPercent(Math.abs(tier.difference_pct))}
                          </span>
                        )}
                        {tier.is_overweight && (
                          <span className="flex items-center gap-1">
                            <AlertCircle className="h-3 w-3" />
                            Overweight by {formatPercent(tier.difference_pct)}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Holdings Table */}
          <Card>
            <CardHeader>
              <CardTitle>Holdings</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingAllocation ? (
                <div className="space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : allocation?.positions?.length ? (
                <div className="max-h-[400px] overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ticker</TableHead>
                        <TableHead>Tier</TableHead>
                        <TableHead className="text-right">Shares</TableHead>
                        <TableHead className="text-right">Cost</TableHead>
                        <TableHead className="text-right">Value</TableHead>
                        <TableHead className="text-right">Gain/Loss</TableHead>
                        <TableHead className="text-right">Weight</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {allocation.positions.map((pos) => (
                        <TableRow
                          key={pos.ticker}
                          className="cursor-pointer"
                          onClick={() => navigate(`/company/${pos.ticker}`)}
                        >
                          <TableCell className="font-medium">{pos.ticker}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{tierLabels[pos.tier]}</Badge>
                          </TableCell>
                          <TableCell className="text-right">{pos.total_shares}</TableCell>
                          <TableCell className="text-right">
                            {formatCurrency(pos.total_cost)}
                          </TableCell>
                          <TableCell className="text-right">
                            {formatCurrency(pos.current_value)}
                          </TableCell>
                          <TableCell className={cn('text-right', getChangeColor(pos.gain_loss))}>
                            {pos.gain_loss >= 0 ? '+' : ''}
                            {formatPercent(pos.gain_loss_pct)}
                          </TableCell>
                          <TableCell className="text-right">
                            {formatPercent(pos.weight_pct)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-center py-12 text-muted-foreground">
                  No holdings yet. Add your first position!
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Add Position Tab */}
        <TabsContent value="add">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Add Position
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 max-w-md">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Ticker</label>
                  <Input
                    value={newTicker}
                    onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                    placeholder="AAPL"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Shares</label>
                  <Input
                    type="number"
                    value={newShares}
                    onChange={(e) => setNewShares(e.target.value)}
                    placeholder="10"
                    min="0"
                    step="0.0001"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Total Cost ($)</label>
                  <Input
                    type="number"
                    value={newCost}
                    onChange={(e) => setNewCost(e.target.value)}
                    placeholder="1500.00"
                    min="0"
                    step="0.01"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Purchase Date</label>
                  <Input
                    type="date"
                    value={newDate}
                    onChange={(e) => setNewDate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tier</label>
                  <Select
                    value={newTier}
                    onChange={(e) => setNewTier(e.target.value as Tier)}
                    options={tierOptions}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Notes (optional)</label>
                  <Input
                    value={newNotes}
                    onChange={(e) => setNewNotes(e.target.value)}
                    placeholder="Optional notes..."
                  />
                </div>
                <Button
                  onClick={handleAddPosition}
                  disabled={!newTicker || !newShares || !newCost || !newDate || addHoldingMutation.isPending}
                  className="mt-2"
                >
                  {addHoldingMutation.isPending ? 'Adding...' : 'Add Position'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Deploy Tab */}
        <TabsContent value="deploy" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Deploy Capital
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 items-end max-w-md">
                <div className="flex-1 space-y-2">
                  <label className="text-sm font-medium">Amount to Deploy ($)</label>
                  <Input
                    type="number"
                    value={deployAmount}
                    onChange={(e) => setDeployAmount(e.target.value)}
                    placeholder="1000"
                    min="0"
                    step="100"
                  />
                </div>
                <Button
                  onClick={handleDeploy}
                  disabled={!deployAmount || parseFloat(deployAmount) <= 0 || deployMutation.isPending}
                >
                  {deployMutation.isPending ? 'Calculating...' : 'Get Recommendations'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recommendations */}
          {deployMutation.data && (
            <>
              {/* Summary */}
              <div className="grid gap-4 md:grid-cols-3">
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-sm text-muted-foreground">To Deploy</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(deployMutation.data.available_capital)}
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-sm text-muted-foreground">Deployed</p>
                    <p className="text-xl font-bold text-success">
                      {formatCurrency(deployMutation.data.total_deployed)}
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-sm text-muted-foreground">Remaining</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(deployMutation.data.remaining_cash)}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Reasoning */}
              {deployMutation.data.reasoning.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-1">
                      {deployMutation.data.reasoning.map((reason, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-primary">•</span>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle>Buy Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  {deployMutation.data.recommendations.length > 0 ? (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {deployMutation.data.recommendations.map((rec) => (
                        <Card
                          key={rec.ticker}
                          className="cursor-pointer hover:border-primary/50 transition-colors"
                          onClick={() => navigate(`/company/${rec.ticker}`)}
                        >
                          <CardContent className="pt-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-bold text-lg">{rec.ticker}</span>
                              <Badge variant="secondary">{tierLabels[rec.tier]}</Badge>
                            </div>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Amount</span>
                                <span className="font-medium text-success">
                                  {formatCurrency(rec.amount)}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Est. Shares</span>
                                <span>{rec.shares_estimate.toFixed(2)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Score</span>
                                <span>{rec.score.toFixed(0)}</span>
                              </div>
                            </div>
                            <p className="text-xs text-muted-foreground mt-3">{rec.reason}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center py-8 text-muted-foreground">
                      No recommendations available. Your portfolio may already be well-balanced.
                    </p>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
