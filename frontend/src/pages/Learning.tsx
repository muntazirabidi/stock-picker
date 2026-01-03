import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  BookOpen,
  TrendingUp,
  Shield,
  DollarSign,
  BarChart3,
  Target,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Gem,
  Lightbulb,
  ArrowRight,
  Zap,
  Scale,
  Building2,
  CircleDollarSign,
  PiggyBank,
  ChevronRight,
  Info,
  TrendingDown,
  Percent,
} from 'lucide-react'
import { cn } from '@/lib/utils'

type TabId = 'fundamentals' | 'quality' | 'growth' | 'valuation' | 'framework'

const tabs: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: 'fundamentals', label: 'Fundamentals', icon: BookOpen },
  { id: 'quality', label: 'Quality', icon: Gem },
  { id: 'growth', label: 'Growth', icon: TrendingUp },
  { id: 'valuation', label: 'Valuation', icon: DollarSign },
  { id: 'framework', label: 'Framework', icon: Target },
]

function InsightBox({ children, type = 'tip' }: { children: React.ReactNode; type?: 'tip' | 'warning' | 'key' }) {
  const styles = {
    tip: 'bg-primary/5 border-primary/20 text-primary',
    warning: 'bg-amber-500/5 border-amber-500/20 text-amber-400',
    key: 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400',
  }
  const icons = {
    tip: Lightbulb,
    warning: AlertTriangle,
    key: Zap,
  }
  const Icon = icons[type]

  return (
    <div className={cn('flex gap-3 p-4 rounded-xl border', styles[type])}>
      <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
      <div className="text-sm text-foreground/90 leading-relaxed">{children}</div>
    </div>
  )
}

function MetricExplainer({
  name,
  oneLiner,
  formula,
  intuition,
  good,
  bad,
  example,
}: {
  name: string
  oneLiner: string
  formula: string
  intuition: string
  good: string
  bad: string
  example?: string
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className={cn(
        'group rounded-xl border border-border/50 bg-card/50 overflow-hidden transition-all duration-200',
        expanded ? 'ring-1 ring-primary/30' : 'hover:border-border'
      )}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 text-left flex items-start justify-between gap-4"
      >
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-base mb-1">{name}</h4>
          <p className="text-sm text-muted-foreground">{oneLiner}</p>
        </div>
        <ChevronRight
          className={cn(
            'h-5 w-5 text-muted-foreground transition-transform flex-shrink-0 mt-1',
            expanded && 'rotate-90'
          )}
        />
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-border/50 pt-4 animate-fade-in">
          <div>
            <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5">Formula</p>
            <code className="text-sm bg-accent/50 px-3 py-1.5 rounded-lg font-mono block">{formula}</code>
          </div>

          <div>
            <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5">Intuition</p>
            <p className="text-sm leading-relaxed">{intuition}</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
              <p className="text-xs font-medium text-emerald-400 mb-1">Good</p>
              <p className="text-sm">{good}</p>
            </div>
            <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/20">
              <p className="text-xs font-medium text-red-400 mb-1">Concerning</p>
              <p className="text-sm">{bad}</p>
            </div>
          </div>

          {example && (
            <div className="p-3 rounded-lg bg-accent/30 border border-border/50">
              <p className="text-xs font-medium text-muted-foreground mb-1">Real Example</p>
              <p className="text-sm">{example}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Learning() {
  const [activeTab, setActiveTab] = useState<TabId>('fundamentals')

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-4 py-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
          <BookOpen className="h-4 w-4" />
          Learning Center
        </div>
        <h1 className="text-4xl font-bold tracking-tight">
          Master Stock Analysis
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Build the intuition to identify high-quality companies trading at reasonable prices.
          No jargon, just the mental models that matter.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex justify-center">
        <div className="inline-flex gap-1 p-1 rounded-xl bg-accent/50 border border-border/50">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div className="min-h-[600px]">
        {/* Fundamentals Tab */}
        {activeTab === 'fundamentals' && (
          <div className="space-y-8 animate-fade-in">
            {/* Core Philosophy */}
            <section className="space-y-4">
              <h2 className="text-2xl font-bold">The Core Idea</h2>
              <Card className="border-primary/20 bg-gradient-to-br from-card to-primary/5">
                <CardContent className="p-6">
                  <p className="text-xl leading-relaxed">
                    A stock is a <span className="text-primary font-semibold">fractional ownership</span> of a real business.
                    When you buy shares, you're not buying a ticker symbol—you're buying
                    a piece of a company's future earnings.
                  </p>
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-5 rounded-xl border border-border/50 bg-card/50 space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-emerald-500/10">
                      <Building2 className="h-5 w-5 text-emerald-400" />
                    </div>
                    <h3 className="font-semibold">What Makes a Business Valuable?</h3>
                  </div>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span>Generates more cash than it consumes</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span>Can reinvest that cash at high returns</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span>Has durable competitive advantages</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span>Growing its earnings over time</span>
                    </li>
                  </ul>
                </div>

                <div className="p-5 rounded-xl border border-border/50 bg-card/50 space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-amber-500/10">
                      <Scale className="h-5 w-5 text-amber-400" />
                    </div>
                    <h3 className="font-semibold">The Price You Pay Matters</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Even a great business is a bad investment if you overpay. Your
                    returns depend on two things:
                  </p>
                  <div className="text-sm space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-blue-400 font-mono">1.</span>
                      <span>How fast the business grows its earnings</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-blue-400 font-mono">2.</span>
                      <span>The multiple you pay for those earnings</span>
                    </div>
                  </div>
                </div>
              </div>

              <InsightBox type="key">
                <strong>The Goal:</strong> Find businesses earning high returns on capital, growing those
                earnings consistently, and trading at prices that don't assume perfection.
              </InsightBox>
            </section>

            {/* Financial Statements */}
            <section className="space-y-4">
              <h2 className="text-2xl font-bold">The Three Financial Statements</h2>
              <p className="text-muted-foreground">
                All the metrics in this system come from three reports every public company must publish.
              </p>

              <div className="grid gap-4">
                <Card className="border-blue-500/20 overflow-hidden">
                  <div className="flex">
                    <div className="w-1.5 bg-blue-500" />
                    <div className="flex-1 p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-lg">Income Statement</h3>
                        <Badge variant="outline" className="text-blue-400 border-blue-500/30">Profitability</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Shows how much the company earned (or lost) over a period. Think of it as a video
                        of the business performance.
                      </p>
                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs px-2 py-1 rounded-md bg-blue-500/10 text-blue-300">Revenue</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-blue-500/10 text-blue-300">Gross Profit</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-blue-500/10 text-blue-300">Operating Income</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-blue-500/10 text-blue-300">Net Income</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card className="border-emerald-500/20 overflow-hidden">
                  <div className="flex">
                    <div className="w-1.5 bg-emerald-500" />
                    <div className="flex-1 p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-lg">Balance Sheet</h3>
                        <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">Strength</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        A snapshot of what the company owns (assets) and owes (liabilities) at a moment in time.
                        Like a photo of financial health.
                      </p>
                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-300">Cash</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-300">Debt</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-300">Equity</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-300">Assets</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card className="border-violet-500/20 overflow-hidden">
                  <div className="flex">
                    <div className="w-1.5 bg-violet-500" />
                    <div className="flex-1 p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-lg">Cash Flow Statement</h3>
                        <Badge variant="outline" className="text-violet-400 border-violet-500/30">Reality Check</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Shows actual cash moving in and out. Harder to manipulate than earnings.
                        The ground truth of business health.
                      </p>
                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs px-2 py-1 rounded-md bg-violet-500/10 text-violet-300">Operating Cash Flow</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-violet-500/10 text-violet-300">CapEx</span>
                        <span className="text-xs px-2 py-1 rounded-md bg-violet-500/10 text-violet-300">Free Cash Flow</span>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>

              <InsightBox type="tip">
                <strong>Pro Tip:</strong> Always look at Free Cash Flow (FCF), not just Net Income.
                FCF = Operating Cash Flow − Capital Expenditures. It's the cash left over after
                keeping the business running—what can actually be returned to shareholders.
              </InsightBox>
            </section>

            {/* Key Concept */}
            <section className="space-y-4">
              <h2 className="text-2xl font-bold">The Power of Compounding</h2>
              <div className="p-6 rounded-xl border border-border/50 bg-card/50">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <p className="text-muted-foreground">
                      A "compounder" is a business that can reinvest its profits at high rates
                      of return year after year. This creates exponential growth.
                    </p>
                    <div className="p-4 rounded-lg bg-accent/30 font-mono text-sm space-y-1">
                      <p className="text-muted-foreground">$100 invested at 15% ROIC:</p>
                      <p>Year 5: <span className="text-emerald-400">$201</span></p>
                      <p>Year 10: <span className="text-emerald-400">$405</span></p>
                      <p>Year 20: <span className="text-emerald-400">$1,637</span></p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <p className="text-muted-foreground">
                      The key is finding companies that can sustain high returns. Most businesses
                      see returns decline as competitors enter.
                    </p>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">What enables sustained high returns?</p>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        <li>• Network effects (more users = more valuable)</li>
                        <li>• High switching costs (hard to leave)</li>
                        <li>• Economies of scale (bigger = cheaper)</li>
                        <li>• Brand power (pricing power)</li>
                        <li>• Regulatory moats (licenses, patents)</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* Quality Tab */}
        {activeTab === 'quality' && (
          <div className="space-y-8 animate-fade-in">
            <section className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500">
                  <Gem className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Quality Metrics</h2>
                  <p className="text-muted-foreground">How efficiently does the business generate profits?</p>
                </div>
              </div>

              <InsightBox type="key">
                Quality metrics answer one question: <strong>"Is this a good business?"</strong> A high-quality
                business generates more profit per dollar invested, giving it more options—reinvest, acquire,
                pay dividends, or buy back shares.
              </InsightBox>
            </section>

            <section className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center text-xs font-bold text-blue-400">1</span>
                Return Metrics
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                The most important metrics. They measure how much profit the company generates relative to capital invested.
              </p>

              <div className="space-y-3">
                <MetricExplainer
                  name="ROIC — Return on Invested Capital"
                  oneLiner="The single best measure of business quality"
                  formula="NOPAT ÷ Invested Capital"
                  intuition="Imagine you opened a coffee shop and invested $100,000. If the shop generates $20,000 in after-tax profit, your ROIC is 20%. The higher this number, the better the business at turning capital into profits. Companies with high ROIC can grow faster without needing to constantly raise money."
                  good="Above 15%. Elite businesses sustain 20%+"
                  bad="Below 8%. Barely covering cost of capital"
                  example="Apple's ROIC ~50%. For every $1 invested in the business, it generates $0.50 in annual profit. Compare to GM at ~5%."
                />

                <MetricExplainer
                  name="ROE — Return on Equity"
                  oneLiner="Profit generated from shareholder money"
                  formula="Net Income ÷ Shareholders' Equity"
                  intuition="Similar to ROIC but only looks at shareholder money (ignoring debt). A company can boost ROE by taking on debt, so always compare with ROIC. If ROE is much higher than ROIC, the company is using financial leverage."
                  good="Above 15% with low debt"
                  bad="Below 10%, or high only due to debt"
                  example="A company with ROE 25% but ROIC 10% is likely heavily leveraged—risky in downturns."
                />
              </div>
            </section>

            <section className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center text-xs font-bold text-blue-400">2</span>
                Margin Metrics
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                How much of each revenue dollar becomes profit at each stage.
              </p>

              <div className="space-y-3">
                <MetricExplainer
                  name="Gross Margin"
                  oneLiner="Revenue minus the direct cost of goods sold"
                  formula="(Revenue − COGS) ÷ Revenue"
                  intuition="If you sell a phone for $1,000 and the parts + assembly cost $400, gross margin is 60%. High gross margins indicate pricing power and competitive advantage. Software businesses often have 70-80% gross margins because there's nearly zero cost per additional user."
                  good="Above 40% (sector dependent)"
                  bad="Below 20% means commodity business"
                  example="Microsoft: 69%. Walmart: 24%. Higher margin = more room for error and reinvestment."
                />

                <MetricExplainer
                  name="Operating Margin"
                  oneLiner="Profit after running the business"
                  formula="Operating Income ÷ Revenue"
                  intuition="After paying for the product (COGS), you still have to pay rent, salaries, marketing, R&D. Operating margin shows what's left. A company with high gross margin but low operating margin is spending too much on operations."
                  good="Above 15% shows efficiency"
                  bad="Below 5% means thin margins"
                />

                <MetricExplainer
                  name="FCF Margin"
                  oneLiner="Actual cash profit as a percentage of revenue"
                  formula="Free Cash Flow ÷ Revenue"
                  intuition="This is the real profit. Net income can be manipulated with accounting, but cash is cash. FCF margin shows what percentage of revenue turns into actual cash you could take out of the business."
                  good="Above 10% is strong"
                  bad="Negative means burning cash"
                  example="A company with 15% net margin but 5% FCF margin might have accounting profits but is reinvesting heavily or has working capital issues."
                />
              </div>
            </section>

            <InsightBox type="warning">
              <strong>Watch for margin trends.</strong> A company with declining margins may face
              increasing competition. Look at 3-5 year trends, not just the latest number.
            </InsightBox>
          </div>
        )}

        {/* Growth Tab */}
        {activeTab === 'growth' && (
          <div className="space-y-8 animate-fade-in">
            <section className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Growth Metrics</h2>
                  <p className="text-muted-foreground">How fast is the business expanding?</p>
                </div>
              </div>

              <InsightBox type="key">
                Growth creates value only when returns exceed the cost of capital. A company growing
                revenue 30% but destroying value with each sale is burning shareholder money.
                <strong> Growth + Quality = Compounding</strong>.
              </InsightBox>
            </section>

            <section className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-xs font-bold text-emerald-400">1</span>
                Revenue Growth
              </h3>

              <div className="space-y-3">
                <MetricExplainer
                  name="Revenue Growth (1 Year)"
                  oneLiner="Most recent growth rate"
                  formula="(Revenue_now − Revenue_last_year) ÷ Revenue_last_year"
                  intuition="Shows current momentum. Is the business accelerating or decelerating? A company that grew 40% last year but only 15% this year may be hitting market saturation."
                  good="10%+ for established, 20%+ for growth"
                  bad="Negative or decelerating sharply"
                />

                <MetricExplainer
                  name="Revenue CAGR (3-5 Year)"
                  oneLiner="Compound annual growth over multiple years"
                  formula="(Revenue_now ÷ Revenue_n_years_ago)^(1/n) − 1"
                  intuition="Smooths out year-to-year volatility. A 3-year CAGR of 15% means the company has consistently grown at 15% annually. This is more reliable than single-year growth which can be lumpy."
                  good="10%+ sustained over 3-5 years"
                  bad="Below 5% suggests mature/declining"
                  example="A company with 50% growth one year and -20% the next has a CAGR of ~10%—much less impressive than it first appeared."
                />
              </div>
            </section>

            <section className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-xs font-bold text-emerald-400">2</span>
                Profitability Growth
              </h3>

              <div className="space-y-3">
                <MetricExplainer
                  name="Earnings Growth"
                  oneLiner="Bottom-line profit growth"
                  formula="(EPS_now − EPS_last_year) ÷ EPS_last_year"
                  intuition="Revenue growth is vanity, earnings growth is sanity. A company can grow revenue by selling at a loss—that's not sustainable. Earnings growth should roughly track or exceed revenue growth over time (operating leverage)."
                  good="Tracking or exceeding revenue growth"
                  bad="Growing revenue but shrinking earnings"
                />

                <MetricExplainer
                  name="FCF Growth"
                  oneLiner="Growth in actual cash profits"
                  formula="(FCF_now − FCF_last_year) ÷ FCF_last_year"
                  intuition="The most honest growth metric. Cash can't be faked with accounting tricks. Growing FCF means the business is generating more real profit that can be returned to shareholders or reinvested."
                  good="Positive and growing"
                  bad="Declining while revenue grows"
                />
              </div>
            </section>

            <section className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-xs font-bold text-emerald-400">3</span>
                Growth vs. Profitability Tradeoff
              </h3>

              <Card className="border-border/50 bg-card/50">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-amber-500/10">
                      <Scale className="h-5 w-5 text-amber-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold">Rule of 40</h4>
                      <p className="text-sm text-muted-foreground">Revenue Growth % + FCF Margin % ≥ 40</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    For growth companies that aren't yet profitable, this balances growth against profitability.
                    A company growing 50% with -10% FCF margin (score: 40) is as healthy as one growing 20% with
                    20% FCF margin.
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                      <p className="font-medium text-emerald-400 mb-1">Healthy Balance</p>
                      <p className="text-muted-foreground">30% growth + 15% FCF = 45</p>
                    </div>
                    <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/20">
                      <p className="font-medium text-red-400 mb-1">Concerning</p>
                      <p className="text-muted-foreground">20% growth + 5% FCF = 25</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </section>

            <InsightBox type="warning">
              <strong>Growth is not always good.</strong> Many companies destroy value by growing into
              unprofitable markets or acquisitions. Always ask: "Can growth be sustained? Does it come
              with improving or stable margins?"
            </InsightBox>
          </div>
        )}

        {/* Valuation Tab */}
        {activeTab === 'valuation' && (
          <div className="space-y-8 animate-fade-in">
            <section className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500">
                  <DollarSign className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Valuation Metrics</h2>
                  <p className="text-muted-foreground">Is the current stock price attractive?</p>
                </div>
              </div>

              <InsightBox type="key">
                Valuation is the <strong>price you pay</strong> for a business. Even the best business
                is a bad investment at the wrong price. Conversely, a mediocre business at a
                cheap enough price can be a great investment.
              </InsightBox>
            </section>

            <section className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-violet-500/20 flex items-center justify-center text-xs font-bold text-violet-400">1</span>
                Earnings-Based Metrics
              </h3>

              <div className="space-y-3">
                <MetricExplainer
                  name="P/E Ratio — Price to Earnings"
                  oneLiner="Years of earnings to pay back your investment"
                  formula="Stock Price ÷ Earnings Per Share"
                  intuition="If a stock is $100 and earns $5/share, P/E is 20. This means you're paying 20 years worth of current earnings. Lower P/E = cheaper. BUT low P/E can mean the market expects declining earnings."
                  good="Below 20 for stable companies"
                  bad="Above 30 requires high growth to justify"
                  example="Market average P/E is historically ~16-17. Tech often trades at 25-35x due to growth expectations."
                />

                <MetricExplainer
                  name="PEG Ratio — P/E to Growth"
                  oneLiner="P/E adjusted for growth rate"
                  formula="P/E Ratio ÷ Earnings Growth Rate"
                  intuition="A stock with P/E 30 growing 30% yearly has PEG of 1.0—fairly valued for its growth. PEG under 1 suggests growth is underpriced. But be careful: a high P/E stock can have low PEG if growth projections are aggressive."
                  good="Below 1.5"
                  bad="Above 2.0"
                />

                <MetricExplainer
                  name="Earnings Yield"
                  oneLiner="Inverse of P/E—your 'return' from buying"
                  formula="EPS ÷ Stock Price (or 1/PE)"
                  intuition="Compare this to bond yields. If a stock has 5% earnings yield and bonds pay 4%, stocks offer a small premium for their risk. If stocks yield 8% while bonds pay 4%, stocks look attractive."
                  good="Above 5-6%"
                  bad="Below 3% (expensive)"
                />
              </div>
            </section>

            <section className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-violet-500/20 flex items-center justify-center text-xs font-bold text-violet-400">2</span>
                Cash Flow-Based Metrics
              </h3>

              <div className="space-y-3">
                <MetricExplainer
                  name="FCF Yield — Free Cash Flow Yield"
                  oneLiner="Cash return on your investment"
                  formula="Free Cash Flow ÷ Market Cap"
                  intuition="This is arguably the most important valuation metric. It tells you what percentage cash return you'd get if the company paid out all its FCF. A 5% FCF yield means for every $100 invested, the company generates $5 in cash."
                  good="Above 5%"
                  bad="Below 2%"
                  example="A company with $1B market cap and $80M FCF has 8% FCF yield—strong value signal."
                />

                <MetricExplainer
                  name="EV/EBITDA — Enterprise Value to EBITDA"
                  oneLiner="Total company value relative to operating profit"
                  formula="(Market Cap + Debt − Cash) ÷ EBITDA"
                  intuition="Unlike P/E which only looks at equity, this considers the whole company (debt included). Useful for comparing companies with different capital structures. Often used in M&A—a buyer would pay for the whole enterprise."
                  good="Below 12x"
                  bad="Above 15x"
                />
              </div>
            </section>

            <section className="space-y-4">
              <h3 className="text-lg font-semibold">The Valuation Trap</h3>

              <div className="grid md:grid-cols-2 gap-4">
                <Card className="border-red-500/20 bg-red-500/5">
                  <CardContent className="p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingDown className="h-5 w-5 text-red-400" />
                      <h4 className="font-semibold text-red-400">Value Trap</h4>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      A stock that looks cheap but keeps getting cheaper. The low valuation reflects
                      real problems: declining business, disruption, or structural issues.
                    </p>
                    <div className="text-sm space-y-1">
                      <p className="flex items-center gap-2">
                        <XCircle className="h-3.5 w-3.5 text-red-400" />
                        Low P/E + declining revenue
                      </p>
                      <p className="flex items-center gap-2">
                        <XCircle className="h-3.5 w-3.5 text-red-400" />
                        High yield + shrinking business
                      </p>
                      <p className="flex items-center gap-2">
                        <XCircle className="h-3.5 w-3.5 text-red-400" />
                        "Cheap" for years with no catalyst
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-emerald-500/20 bg-emerald-500/5">
                  <CardContent className="p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <Gem className="h-5 w-5 text-emerald-400" />
                      <h4 className="font-semibold text-emerald-400">True Value</h4>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      A quality business temporarily mispriced. The low valuation is an opportunity
                      because the business fundamentals remain strong.
                    </p>
                    <div className="text-sm space-y-1">
                      <p className="flex items-center gap-2">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        Low P/E + stable/growing revenue
                      </p>
                      <p className="flex items-center gap-2">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        Strong FCF + temporary headwinds
                      </p>
                      <p className="flex items-center gap-2">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        High ROIC + market overreaction
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </section>

            <InsightBox type="tip">
              <strong>Cheap ≠ Good. Expensive ≠ Bad.</strong> Always pair valuation metrics with quality
              metrics. The goal is high quality at reasonable prices—not just low multiples.
            </InsightBox>
          </div>
        )}

        {/* Framework Tab */}
        {activeTab === 'framework' && (
          <div className="space-y-8 animate-fade-in">
            <section className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-primary to-indigo-500">
                  <Target className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">The Scoring Framework</h2>
                  <p className="text-muted-foreground">How this system ranks and scores stocks</p>
                </div>
              </div>
            </section>

            {/* How It Works */}
            <section className="space-y-4">
              <h3 className="text-xl font-semibold">How Scoring Works</h3>

              <div className="grid md:grid-cols-4 gap-4">
                {[
                  {
                    step: '1',
                    title: 'Calculate',
                    desc: 'Compute ~20 metrics from financial statements',
                    color: 'blue',
                  },
                  {
                    step: '2',
                    title: 'Rank',
                    desc: 'Percentile rank each metric vs all stocks',
                    color: 'emerald',
                  },
                  {
                    step: '3',
                    title: 'Group',
                    desc: 'Average into Quality, Growth, Strength, Valuation',
                    color: 'amber',
                  },
                  {
                    step: '4',
                    title: 'Weight',
                    desc: 'Combine with stage-appropriate weights',
                    color: 'violet',
                  },
                ].map((item) => (
                  <div
                    key={item.step}
                    className={cn(
                      'p-4 rounded-xl border text-center space-y-2',
                      `border-${item.color}-500/20 bg-${item.color}-500/5`
                    )}
                  >
                    <div
                      className={cn(
                        'w-8 h-8 rounded-full mx-auto flex items-center justify-center text-sm font-bold',
                        `bg-${item.color}-500/20 text-${item.color}-400`
                      )}
                    >
                      {item.step}
                    </div>
                    <p className="font-semibold">{item.title}</p>
                    <p className="text-xs text-muted-foreground">{item.desc}</p>
                  </div>
                ))}
              </div>

              <InsightBox type="tip">
                <strong>Percentile ranking means relative scoring.</strong> A score of 75 means "better
                than 75% of stocks in the universe." The same stock will score differently in different
                universes (S&P 500 vs small caps).
              </InsightBox>
            </section>

            {/* Quality-Valuation Matrix */}
            <section className="space-y-4">
              <h3 className="text-xl font-semibold">The Quality-Valuation Matrix</h3>
              <p className="text-muted-foreground">
                This is the core framework. We plot every stock on two axes: how good is the business
                (Quality) and how cheap is the stock (Valuation).
              </p>

              <div className="grid grid-cols-2 gap-3 max-w-2xl mx-auto">
                <div className="p-5 rounded-xl border-2 border-amber-500/30 bg-amber-500/5 text-center">
                  <AlertTriangle className="h-8 w-8 text-amber-400 mx-auto mb-2" />
                  <p className="font-bold text-amber-400">Value Traps</p>
                  <p className="text-xs text-muted-foreground mt-1">Low Quality + Cheap</p>
                  <p className="text-sm mt-2">Cheap for a reason. Avoid.</p>
                </div>
                <div className="p-5 rounded-xl border-2 border-emerald-500/30 bg-emerald-500/5 text-center">
                  <Gem className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
                  <p className="font-bold text-emerald-400">Value Picks</p>
                  <p className="text-xs text-muted-foreground mt-1">High Quality + Cheap</p>
                  <p className="text-sm mt-2">The sweet spot. Buy.</p>
                </div>
                <div className="p-5 rounded-xl border-2 border-red-500/30 bg-red-500/5 text-center">
                  <XCircle className="h-8 w-8 text-red-400 mx-auto mb-2" />
                  <p className="font-bold text-red-400">Avoid</p>
                  <p className="text-xs text-muted-foreground mt-1">Low Quality + Expensive</p>
                  <p className="text-sm mt-2">Worst of both worlds.</p>
                </div>
                <div className="p-5 rounded-xl border-2 border-blue-500/30 bg-blue-500/5 text-center">
                  <TrendingUp className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                  <p className="font-bold text-blue-400">Quality Premium</p>
                  <p className="text-xs text-muted-foreground mt-1">High Quality + Expensive</p>
                  <p className="text-sm mt-2">Great business, wait for dip.</p>
                </div>
              </div>

              <div className="flex items-center justify-center gap-8 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <ArrowRight className="h-4 w-4" />
                  <span>Quality Score (X-axis)</span>
                </div>
                <div className="flex items-center gap-2">
                  <ArrowRight className="h-4 w-4 rotate-[-90deg]" />
                  <span>Valuation Score (Y-axis)</span>
                </div>
              </div>
            </section>

            {/* Company Stages */}
            <section className="space-y-4">
              <h3 className="text-xl font-semibold">Company Lifecycle Stages</h3>
              <p className="text-muted-foreground">
                Different companies need different scoring weights. A growth company shouldn't be
                penalized for low current profitability if it's investing for future growth.
              </p>

              <div className="grid md:grid-cols-2 gap-4">
                <Card className="border-l-4 border-l-emerald-500">
                  <CardContent className="p-5">
                    <h4 className="font-bold text-emerald-400 mb-2">Compounder</h4>
                    <p className="text-sm text-muted-foreground mb-3">
                      Proven business, still growing. The ideal long-term holding.
                    </p>
                    <div className="text-xs space-y-1">
                      <p>• FCF Positive + Revenue Growth ≥10%</p>
                      <p>• Weights: Growth 30%, Valuation 30%</p>
                      <p>• Examples: MSFT, AAPL, COST</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-l-4 border-l-blue-500">
                  <CardContent className="p-5">
                    <h4 className="font-bold text-blue-400 mb-2">Mature</h4>
                    <p className="text-sm text-muted-foreground mb-3">
                      Stable cash generators. Focus on quality and strength.
                    </p>
                    <div className="text-xs space-y-1">
                      <p>• FCF Positive + Revenue Growth &lt;10%</p>
                      <p>• Weights: Quality 35%, Strength 25%</p>
                      <p>• Examples: JNJ, PG, KO</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-l-4 border-l-amber-500">
                  <CardContent className="p-5">
                    <h4 className="font-bold text-amber-400 mb-2">Growth</h4>
                    <p className="text-sm text-muted-foreground mb-3">
                      Reinvesting everything. Evaluate on unit economics and runway.
                    </p>
                    <div className="text-xs space-y-1">
                      <p>• FCF Negative + Gross Margin &gt;40%</p>
                      <p>• Focus: Rule of 40, Gross Margin Trend</p>
                      <p>• Examples: Early SNOW, CRWD</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-l-4 border-l-slate-500">
                  <CardContent className="p-5">
                    <h4 className="font-bold text-slate-400 mb-2">Speculative</h4>
                    <p className="text-sm text-muted-foreground mb-3">
                      Doesn't fit categories. Requires manual due diligence.
                    </p>
                    <div className="text-xs space-y-1">
                      <p>• Turnarounds, special situations</p>
                      <p>• Quantitative scores less reliable</p>
                      <p>• Very small positions or avoid</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </section>

            <InsightBox type="warning">
              <strong>Scores are not buy signals.</strong> They identify fundamentally strong companies at
              attractive prices, but you should always understand the business, read recent news, and
              consider qualitative factors before investing.
            </InsightBox>
          </div>
        )}
      </div>
    </div>
  )
}
