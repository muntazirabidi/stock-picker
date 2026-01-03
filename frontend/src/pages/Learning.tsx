import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  BookOpen,
  TrendingUp,
  Shield,
  DollarSign,
  BarChart3,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Gem,
  Layers,
  Calculator,
  PieChart,
} from 'lucide-react'

function MetricCard({
  name,
  formula,
  interpretation,
  goodValue,
  icon: Icon,
}: {
  name: string
  formula: string
  interpretation: string
  goodValue: string
  icon: React.ElementType
}) {
  return (
    <Card className="bg-card/50 backdrop-blur border-border/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Icon className="h-4 w-4 text-primary" />
          {name}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <div>
          <span className="text-muted-foreground">Formula: </span>
          <code className="bg-slate-800 px-2 py-0.5 rounded text-xs">{formula}</code>
        </div>
        <p className="text-muted-foreground">{interpretation}</p>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
            Good: {goodValue}
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}

function StageCard({
  stage,
  criteria,
  color,
  examples,
  strategy,
}: {
  stage: string
  criteria: string[]
  color: string
  examples: string
  strategy: string
}) {
  return (
    <Card className={`bg-card/50 backdrop-blur border-l-4 ${color}`}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{stage}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <p className="text-sm font-medium text-muted-foreground mb-1">Criteria:</p>
          <ul className="text-sm space-y-1">
            {criteria.map((c, i) => (
              <li key={i} className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-emerald-400" />
                {c}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-sm font-medium text-muted-foreground">Examples: </p>
          <p className="text-sm">{examples}</p>
        </div>
        <div>
          <p className="text-sm font-medium text-muted-foreground">Strategy: </p>
          <p className="text-sm text-primary">{strategy}</p>
        </div>
      </CardContent>
    </Card>
  )
}

export default function Learning() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-gradient-to-br from-primary to-blue-600">
          <BookOpen className="h-8 w-8 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Learning Center</h1>
          <p className="text-muted-foreground">
            Understand the metrics, scoring system, and value investing strategy
          </p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="bg-card/50 backdrop-blur border border-border/50">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="quality">Quality</TabsTrigger>
          <TabsTrigger value="growth">Growth</TabsTrigger>
          <TabsTrigger value="strength">Strength</TabsTrigger>
          <TabsTrigger value="valuation">Valuation</TabsTrigger>
          <TabsTrigger value="scoring">Scoring</TabsTrigger>
          <TabsTrigger value="value">Value Picks</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                Investment Philosophy
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-lg">
                Find <span className="text-emerald-400 font-semibold">high-quality companies</span> trading at{' '}
                <span className="text-blue-400 font-semibold">reasonable valuations</span> before they become mega-caps.
              </p>
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                  <h4 className="font-semibold text-emerald-400 mb-2">What We Want</h4>
                  <ul className="space-y-1 text-sm">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-emerald-400" />
                      High returns on capital (ROIC &gt; 15%)
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-emerald-400" />
                      Consistent revenue growth (10%+ CAGR)
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-emerald-400" />
                      Strong free cash flow generation
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-emerald-400" />
                      Low debt, strong balance sheet
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-emerald-400" />
                      Reasonable valuation vs growth
                    </li>
                  </ul>
                </div>
                <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                  <h4 className="font-semibold text-red-400 mb-2">What We Avoid</h4>
                  <ul className="space-y-1 text-sm">
                    <li className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-400" />
                      Low quality + cheap = Value Traps
                    </li>
                    <li className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-400" />
                      High debt / weak balance sheets
                    </li>
                    <li className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-400" />
                      Declining revenues / market share
                    </li>
                    <li className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-400" />
                      Excessive stock dilution
                    </li>
                    <li className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-400" />
                      Overpaying for hype stocks
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Company Stages */}
          <div>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Layers className="h-5 w-5 text-primary" />
              Company Lifecycle Stages
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <StageCard
                stage="Compounder"
                criteria={['Free Cash Flow Positive', 'Revenue Growth ≥ 10%', 'Proven business model']}
                color="border-emerald-500"
                examples="MSFT, AAPL, COST, FICO"
                strategy="Core holdings - buy and hold for years"
              />
              <StageCard
                stage="Mature"
                criteria={['Free Cash Flow Positive', 'Revenue Growth < 10%', 'Stable, predictable']}
                color="border-blue-500"
                examples="JNJ, PG, KO, WMT"
                strategy="Dividend reinvestment, defensive"
              />
              <StageCard
                stage="Growth"
                criteria={['FCF Negative (reinvesting)', 'Gross Margin > 40%', 'High revenue growth']}
                color="border-amber-500"
                examples="Early-stage SaaS, SNOW, CRWD"
                strategy="Smaller positions, higher risk/reward"
              />
              <StageCard
                stage="Speculative"
                criteria={['Doesn\'t fit other categories', 'Requires manual review', 'Higher uncertainty']}
                color="border-slate-500"
                examples="Turnarounds, special situations"
                strategy="Very small positions or avoid"
              />
            </div>
          </div>

          {/* Scoring Overview */}
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5 text-primary" />
                How Scoring Works
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-muted-foreground">
                  Each stock is scored 0-100 based on <strong>percentile ranking</strong> against all other stocks in the universe.
                  A score of 75 means the stock is better than 75% of peers in that metric.
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border/50">
                        <th className="text-left py-2 px-3">Category</th>
                        <th className="text-left py-2 px-3">Metrics Used</th>
                        <th className="text-center py-2 px-3">Mature</th>
                        <th className="text-center py-2 px-3">Compounder</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border/30">
                        <td className="py-2 px-3 font-medium text-blue-400">Quality</td>
                        <td className="py-2 px-3 text-muted-foreground">ROIC, ROE, Margins, FCF Margin</td>
                        <td className="py-2 px-3 text-center">35%</td>
                        <td className="py-2 px-3 text-center">25%</td>
                      </tr>
                      <tr className="border-b border-border/30">
                        <td className="py-2 px-3 font-medium text-emerald-400">Growth</td>
                        <td className="py-2 px-3 text-muted-foreground">Revenue Growth 1Y, 3Y, FCF Growth</td>
                        <td className="py-2 px-3 text-center">15%</td>
                        <td className="py-2 px-3 text-center">30%</td>
                      </tr>
                      <tr className="border-b border-border/30">
                        <td className="py-2 px-3 font-medium text-amber-400">Strength</td>
                        <td className="py-2 px-3 text-muted-foreground">Current Ratio, Debt/Equity</td>
                        <td className="py-2 px-3 text-center">25%</td>
                        <td className="py-2 px-3 text-center">15%</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-medium text-purple-400">Valuation</td>
                        <td className="py-2 px-3 text-muted-foreground">P/E, EV/EBITDA, FCF Yield</td>
                        <td className="py-2 px-3 text-center">25%</td>
                        <td className="py-2 px-3 text-center font-semibold text-primary">30%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-sm text-muted-foreground">
                  <strong>Note:</strong> Compounders get the highest valuation weight (30%) because overpaying for growth stocks destroys long-term returns.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Quality Tab */}
        <TabsContent value="quality" className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-blue-500/10">
              <TrendingUp className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Quality Metrics</h2>
              <p className="text-sm text-muted-foreground">Measures how efficiently a company generates profits</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <MetricCard
              name="ROIC (Return on Invested Capital)"
              formula="NOPAT / Invested Capital"
              interpretation="How much profit the company generates for each dollar invested. The single best measure of business quality."
              goodValue="> 15%"
              icon={TrendingUp}
            />
            <MetricCard
              name="ROE (Return on Equity)"
              formula="Net Income / Shareholders Equity"
              interpretation="Profit generated from shareholder money. Can be inflated by debt, so use with ROIC."
              goodValue="> 15%"
              icon={TrendingUp}
            />
            <MetricCard
              name="Gross Margin"
              formula="(Revenue - COGS) / Revenue"
              interpretation="Pricing power and competitive advantage. Higher margins = harder to compete with."
              goodValue="> 40%"
              icon={TrendingUp}
            />
            <MetricCard
              name="Operating Margin"
              formula="Operating Income / Revenue"
              interpretation="Profitability after operating costs. Shows operational efficiency."
              goodValue="> 15%"
              icon={TrendingUp}
            />
            <MetricCard
              name="Net Margin"
              formula="Net Income / Revenue"
              interpretation="Bottom-line profitability after all expenses, taxes, and interest."
              goodValue="> 10%"
              icon={TrendingUp}
            />
            <MetricCard
              name="FCF Margin"
              formula="Free Cash Flow / Revenue"
              interpretation="Cash generation efficiency. FCF is what's left after all capex - the real profit."
              goodValue="> 10%"
              icon={TrendingUp}
            />
          </div>

          <Card className="bg-blue-500/5 border-blue-500/20">
            <CardContent className="pt-4">
              <p className="text-sm">
                <strong className="text-blue-400">Why Quality Matters:</strong> High-quality companies can reinvest profits at high rates of return,
                creating a compounding effect. A company with 20% ROIC that reinvests all earnings doubles invested capital every 3.5 years.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Growth Tab */}
        <TabsContent value="growth" className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-emerald-500/10">
              <BarChart3 className="h-6 w-6 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Growth Metrics</h2>
              <p className="text-sm text-muted-foreground">Measures how fast the company is expanding</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <MetricCard
              name="Revenue Growth 1Y"
              formula="(Revenue_now - Revenue_1y_ago) / Revenue_1y_ago"
              interpretation="Recent growth momentum. Shows if the company is accelerating or decelerating."
              goodValue="> 10%"
              icon={BarChart3}
            />
            <MetricCard
              name="Revenue CAGR 3Y"
              formula="(Revenue_now / Revenue_3y_ago)^(1/3) - 1"
              interpretation="Compound annual growth rate over 3 years. Smooths out year-to-year volatility."
              goodValue="> 10%"
              icon={BarChart3}
            />
            <MetricCard
              name="Revenue CAGR 5Y"
              formula="(Revenue_now / Revenue_5y_ago)^(1/5) - 1"
              interpretation="Long-term growth trajectory. Shows sustainability of growth."
              goodValue="> 8%"
              icon={BarChart3}
            />
            <MetricCard
              name="Earnings Growth 1Y"
              formula="(EPS_now - EPS_1y_ago) / EPS_1y_ago"
              interpretation="Bottom-line growth. Should generally track revenue growth."
              goodValue="> 10%"
              icon={BarChart3}
            />
            <MetricCard
              name="FCF Growth 1Y"
              formula="(FCF_now - FCF_1y_ago) / FCF_1y_ago"
              interpretation="Cash flow growth. More reliable than earnings as it's harder to manipulate."
              goodValue="> 10%"
              icon={BarChart3}
            />
            <MetricCard
              name="Rule of 40 (SaaS)"
              formula="Revenue Growth % + FCF Margin %"
              interpretation="For growth companies: balances growth vs profitability. Score > 40 is healthy."
              goodValue="> 40"
              icon={BarChart3}
            />
          </div>

          <Card className="bg-emerald-500/5 border-emerald-500/20">
            <CardContent className="pt-4">
              <p className="text-sm">
                <strong className="text-emerald-400">Growth vs Value:</strong> We look for companies growing revenue 10%+ annually,
                but not at any price. The key is finding growth at a reasonable valuation (GARP - Growth At Reasonable Price).
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Strength Tab */}
        <TabsContent value="strength" className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-amber-500/10">
              <Shield className="h-6 w-6 text-amber-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Financial Strength</h2>
              <p className="text-sm text-muted-foreground">Measures balance sheet health and risk</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <MetricCard
              name="Current Ratio"
              formula="Current Assets / Current Liabilities"
              interpretation="Can the company pay short-term obligations? Below 1.0 is a red flag."
              goodValue="> 1.5"
              icon={Shield}
            />
            <MetricCard
              name="Quick Ratio"
              formula="(Cash + Receivables) / Current Liabilities"
              interpretation="More conservative than current ratio - excludes inventory."
              goodValue="> 1.0"
              icon={Shield}
            />
            <MetricCard
              name="Debt to Equity"
              formula="Total Debt / Shareholders Equity"
              interpretation="How much debt vs equity. High debt = higher risk in downturns."
              goodValue="< 0.5"
              icon={Shield}
            />
            <MetricCard
              name="Interest Coverage"
              formula="EBIT / Interest Expense"
              interpretation="Can the company afford its debt payments? Below 3x is concerning."
              goodValue="> 5x"
              icon={Shield}
            />
            <MetricCard
              name="Cash to Debt"
              formula="Cash & Equivalents / Total Debt"
              interpretation="Could the company pay off all debt with cash? Higher is safer."
              goodValue="> 0.5"
              icon={Shield}
            />
            <MetricCard
              name="Net Debt / EBITDA"
              formula="(Total Debt - Cash) / EBITDA"
              interpretation="Years needed to pay off debt with operating profit. Lower is better."
              goodValue="< 2x"
              icon={Shield}
            />
          </div>

          <Card className="bg-amber-500/5 border-amber-500/20">
            <CardContent className="pt-4">
              <p className="text-sm">
                <strong className="text-amber-400">Why Strength Matters:</strong> Companies with strong balance sheets survive recessions,
                can invest during downturns when competitors can't, and have more flexibility for acquisitions or buybacks.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Valuation Tab */}
        <TabsContent value="valuation" className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-purple-500/10">
              <DollarSign className="h-6 w-6 text-purple-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Valuation Metrics</h2>
              <p className="text-sm text-muted-foreground">Measures if the stock price is attractive</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <MetricCard
              name="P/E Ratio"
              formula="Stock Price / Earnings Per Share"
              interpretation="Most common metric. Lower = cheaper. But low P/E can mean low quality."
              goodValue="< 20-25"
              icon={DollarSign}
            />
            <MetricCard
              name="PEG Ratio"
              formula="P/E Ratio / Earnings Growth Rate"
              interpretation="P/E adjusted for growth. PEG < 1 means growth is underpriced."
              goodValue="< 1.5"
              icon={DollarSign}
            />
            <MetricCard
              name="P/S Ratio"
              formula="Market Cap / Revenue"
              interpretation="Price to Sales. Useful when earnings are negative. Lower = cheaper."
              goodValue="< 3"
              icon={DollarSign}
            />
            <MetricCard
              name="P/B Ratio"
              formula="Market Cap / Book Value"
              interpretation="Price to Book. Most useful for asset-heavy businesses (banks, REITs)."
              goodValue="< 3"
              icon={DollarSign}
            />
            <MetricCard
              name="EV/EBITDA"
              formula="Enterprise Value / EBITDA"
              interpretation="Compares total value (debt + equity) to operating profit. Best for M&A comps."
              goodValue="< 12"
              icon={DollarSign}
            />
            <MetricCard
              name="FCF Yield"
              formula="Free Cash Flow / Market Cap"
              interpretation="Your 'return' from buying the stock. Higher = more cash per dollar invested."
              goodValue="> 5%"
              icon={DollarSign}
            />
            <MetricCard
              name="Earnings Yield"
              formula="EPS / Stock Price (inverse of P/E)"
              interpretation="Compare to bond yields. If earnings yield > 10Y Treasury, stocks may be cheap."
              goodValue="> 5%"
              icon={DollarSign}
            />
            <MetricCard
              name="EV/Sales"
              formula="Enterprise Value / Revenue"
              interpretation="Total enterprise value per dollar of sales. Useful for growth companies."
              goodValue="< 4"
              icon={DollarSign}
            />
          </div>

          <Card className="bg-purple-500/5 border-purple-500/20">
            <CardContent className="pt-4">
              <p className="text-sm">
                <strong className="text-purple-400">Valuation Reality:</strong> A "cheap" stock isn't always good (could be a value trap),
                and an "expensive" stock isn't always bad (could be a compounder). The goal is to find quality at a reasonable price,
                not just the lowest P/E.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scoring Tab */}
        <TabsContent value="scoring" className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-primary/10">
              <Calculator className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Scoring System</h2>
              <p className="text-sm text-muted-foreground">How composite scores are calculated</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card className="bg-card/50 backdrop-blur border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Step 1: Calculate Metrics</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <p className="text-muted-foreground">
                  For each company, we calculate ~20 fundamental metrics from financial statements:
                </p>
                <ul className="space-y-1 text-muted-foreground">
                  <li>• Quality: ROIC, ROE, Margins</li>
                  <li>• Growth: Revenue/Earnings growth rates</li>
                  <li>• Strength: Debt ratios, coverage</li>
                  <li>• Valuation: P/E, EV/EBITDA, FCF Yield</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Step 2: Percentile Ranking</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <p className="text-muted-foreground">
                  Each metric is ranked against all other stocks in the universe:
                </p>
                <div className="bg-slate-800/50 rounded-lg p-3 font-mono text-xs">
                  Score 80 = Better than 80% of stocks<br />
                  Score 50 = Average (median)<br />
                  Score 20 = Bottom 20%
                </div>
                <p className="text-muted-foreground">
                  Outliers are winsorized (clipped to 1st-99th percentile) to prevent distortion.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Step 3: Category Scores</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <p className="text-muted-foreground">
                  Metrics are grouped into categories, and category score = average of metric percentiles:
                </p>
                <div className="bg-slate-800/50 rounded-lg p-3 font-mono text-xs">
                  Quality = avg(ROIC_pct, ROE_pct, Margin_pcts)<br />
                  Growth = avg(RevGrowth_pct, FCFGrowth_pct)<br />
                  Strength = avg(CurrentRatio_pct, D/E_pct)<br />
                  Valuation = avg(PE_pct, EVEBITDA_pct, FCFYield_pct)
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Step 4: Composite Score</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <p className="text-muted-foreground">
                  Category scores are weighted by company stage:
                </p>
                <div className="bg-slate-800/50 rounded-lg p-3 font-mono text-xs">
                  <span className="text-emerald-400">Compounder:</span><br />
                  25% Quality + 30% Growth + 15% Strength + <span className="text-primary">30% Valuation</span><br /><br />
                  <span className="text-blue-400">Mature:</span><br />
                  35% Quality + 15% Growth + 25% Strength + 25% Valuation
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-gradient-to-r from-primary/10 to-blue-600/10 border-primary/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-400" />
                Important Notes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>
                <strong>Relative Scoring:</strong> A score of 70 doesn't mean "70% good" - it means better than 70% of the universe.
                If you analyze S&P 500, scores are relative to those 500 stocks.
              </p>
              <p>
                <strong>Universe Matters:</strong> The same stock will have different scores in different universes.
                A mid-cap might score 80 in S&P 500 but 50 in a high-growth universe.
              </p>
              <p>
                <strong>Not a Buy Signal:</strong> High scores indicate fundamental quality, not that you should buy immediately.
                Always consider qualitative factors, news, and your own research.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Value Picks Tab */}
        <TabsContent value="value" className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-emerald-500/10">
              <Gem className="h-6 w-6 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Finding Value Picks</h2>
              <p className="text-sm text-muted-foreground">How to identify undervalued quality stocks</p>
            </div>
          </div>

          {/* Value Matrix */}
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader>
              <CardTitle>The Quality-Valuation Matrix</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2 max-w-2xl mx-auto">
                <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg text-center">
                  <AlertTriangle className="h-6 w-6 text-amber-400 mx-auto mb-2" />
                  <p className="font-semibold text-amber-400">Value Trap Risk</p>
                  <p className="text-xs text-muted-foreground mt-1">Low Quality + Cheap</p>
                  <p className="text-xs mt-2">Cheap for a reason. Declining business, weak moat.</p>
                </div>
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-center">
                  <Gem className="h-6 w-6 text-emerald-400 mx-auto mb-2" />
                  <p className="font-semibold text-emerald-400">Value Pick</p>
                  <p className="text-xs text-muted-foreground mt-1">High Quality + Cheap</p>
                  <p className="text-xs mt-2">The sweet spot! Strong business at discount.</p>
                </div>
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-center">
                  <XCircle className="h-6 w-6 text-red-400 mx-auto mb-2" />
                  <p className="font-semibold text-red-400">Avoid</p>
                  <p className="text-xs text-muted-foreground mt-1">Low Quality + Expensive</p>
                  <p className="text-xs mt-2">Worst of both worlds. No reason to own.</p>
                </div>
                <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg text-center">
                  <TrendingUp className="h-6 w-6 text-blue-400 mx-auto mb-2" />
                  <p className="font-semibold text-blue-400">Quality Premium</p>
                  <p className="text-xs text-muted-foreground mt-1">High Quality + Expensive</p>
                  <p className="text-xs mt-2">Great company, but may be overpriced.</p>
                </div>
              </div>
              <p className="text-center text-sm text-muted-foreground mt-4">
                X-axis: Quality Score | Y-axis: Valuation Score (higher = cheaper)
              </p>
            </CardContent>
          </Card>

          {/* Value Score Formula */}
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader>
              <CardTitle>Value Score Calculation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-800/50 rounded-lg p-4 text-center">
                <p className="text-lg font-mono">
                  <span className="text-emerald-400">Value Score</span> = (
                  <span className="text-blue-400">Quality Score</span> +
                  <span className="text-purple-400">Valuation Score</span>) / 2
                </p>
              </div>
              <p className="text-sm text-muted-foreground">
                The Value Score equally weights quality (how good is the business?) and valuation (how cheap is the stock?).
                A score of 70+ in both metrics identifies the best opportunities.
              </p>
            </CardContent>
          </Card>

          {/* Top Picks Smart Filter Criteria */}
          <Card className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gem className="h-5 w-5 text-emerald-400" />
                "Top Picks" Smart Filter Criteria
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                These are the criteria used by the "Top Picks" button in Value Picks. Each filter has a specific purpose:
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border/50">
                      <th className="text-left py-2 px-3">Filter</th>
                      <th className="text-left py-2 px-3">Value</th>
                      <th className="text-left py-2 px-3">Why This Matters</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-border/30">
                      <td className="py-3 px-3 font-medium text-emerald-400">Value Score</td>
                      <td className="py-3 px-3">≥ 80</td>
                      <td className="py-3 px-3 text-muted-foreground">
                        Combines quality + valuation. Top 20% means excellent fundamentals AND attractive price.
                      </td>
                    </tr>
                    <tr className="border-b border-border/30">
                      <td className="py-3 px-3 font-medium text-blue-400">Quality Score</td>
                      <td className="py-3 px-3">≥ 60</td>
                      <td className="py-3 px-3 text-muted-foreground">
                        Above average business quality. Strong ROIC, margins, FCF generation. Avoids struggling companies.
                      </td>
                    </tr>
                    <tr className="border-b border-border/30">
                      <td className="py-3 px-3 font-medium text-purple-400">P/E Ratio</td>
                      <td className="py-3 px-3">≤ 25</td>
                      <td className="py-3 px-3 text-muted-foreground">
                        Not overpaying for earnings. Market average is ~20. Excludes speculative high P/E stocks.
                      </td>
                    </tr>
                    <tr className="border-b border-border/30">
                      <td className="py-3 px-3 font-medium text-amber-400">PEG Ratio</td>
                      <td className="py-3 px-3">≤ 1.5</td>
                      <td className="py-3 px-3 text-muted-foreground">
                        P/E adjusted for growth. PEG &lt;1 = growth underpriced. Ensures you're not overpaying for growth rate.
                      </td>
                    </tr>
                    <tr>
                      <td className="py-3 px-3 font-medium text-teal-400">FCF Yield</td>
                      <td className="py-3 px-3">≥ 5%</td>
                      <td className="py-3 px-3 text-muted-foreground">
                        Real cash return on investment. 5% means company generates 5¢ cash per $1 you invest. Higher = cheaper.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* PEG Warning */}
          <Card className="bg-amber-500/5 border-amber-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                PEG Ratio: A Common Trap
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>
                <strong className="text-amber-400">Low PEG doesn't always mean cheap!</strong> Here's why:
              </p>
              <div className="bg-slate-800/50 rounded-lg p-3 font-mono text-xs">
                PEG = P/E ÷ Earnings Growth Rate<br /><br />
                Example: Stock with P/E = 70 and Growth = 200%<br />
                PEG = 70 ÷ 200 = 0.35 (looks cheap!)<br /><br />
                But you're still paying 70x earnings!
              </div>
              <p className="text-muted-foreground">
                Always check <strong>Valuation Score</strong> alongside PEG. If PEG is low but Valuation Score is below 50,
                the stock is expensive on traditional metrics but growing fast. High risk if growth slows.
              </p>
            </CardContent>
          </Card>

          {/* Screening Criteria */}
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                Red Flags to Avoid
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-red-400 mb-2">Warning Signs:</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <XCircle className="h-4 w-4 text-red-400 mt-0.5" />
                      <div>
                        <strong>Value Trap:</strong> Low Quality (&lt;40) + High Valuation (&gt;70) = Cheap for a reason
                      </div>
                    </li>
                    <li className="flex items-start gap-2">
                      <XCircle className="h-4 w-4 text-red-400 mt-0.5" />
                      <div>
                        <strong>PEG Mirage:</strong> Low PEG + Low Valuation Score = Expensive but growing fast
                      </div>
                    </li>
                    <li className="flex items-start gap-2">
                      <XCircle className="h-4 w-4 text-red-400 mt-0.5" />
                      <div>
                        <strong>Declining Industries:</strong> Even great numbers in tobacco, coal = structural decline
                      </div>
                    </li>
                    <li className="flex items-start gap-2">
                      <XCircle className="h-4 w-4 text-red-400 mt-0.5" />
                      <div>
                        <strong>Sector Concentration:</strong> Many "top picks" may be from same sector (e.g., insurance)
                      </div>
                    </li>
                    <li className="flex items-start gap-2">
                      <XCircle className="h-4 w-4 text-red-400 mt-0.5" />
                      <div>
                        <strong>Missing Data:</strong> If PEG or other metrics show "—", verify manually before investing
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Portfolio Allocation */}
          <Card className="bg-card/50 backdrop-blur border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5 text-primary" />
                Suggested Portfolio Allocation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/30">
                  <p className="font-bold text-emerald-400 text-2xl">60%</p>
                  <p className="font-semibold">Tier 1: Compounders</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Proven quality companies. Hold for 5+ years. Max 8% per position.
                  </p>
                </div>
                <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
                  <p className="font-bold text-blue-400 text-2xl">30%</p>
                  <p className="font-semibold">Tier 2: Growth</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Higher growth, higher risk. Max 5% per position.
                  </p>
                </div>
                <div className="p-4 bg-amber-500/10 rounded-lg border border-amber-500/30">
                  <p className="font-bold text-amber-400 text-2xl">10%</p>
                  <p className="font-semibold">Tier 3: Opportunistic</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Special situations, ADRs. Max 3% per position.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
