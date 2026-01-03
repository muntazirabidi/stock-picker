import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useCacheStats } from '@/hooks/useSystem'
import {
  BarChart3,
  Building2,
  Briefcase,
  Database,
  HardDrive,
  Clock,
  AlertCircle,
  ArrowRight,
  Sparkles,
  TrendingUp,
  Target,
  Zap,
  LineChart,
  Shield,
} from 'lucide-react'

const navigationCards = [
  {
    title: 'Universe',
    description: 'Score and rank stocks across S&P 500, Nasdaq 100, and custom lists',
    icon: BarChart3,
    path: '/universe',
    gradient: 'from-blue-500 to-cyan-400',
    accent: 'blue',
    stats: '500+ stocks',
  },
  {
    title: 'Company Analysis',
    description: 'Deep fundamental analysis with quality, growth & valuation metrics',
    icon: Building2,
    path: '/company',
    gradient: 'from-emerald-500 to-teal-400',
    accent: 'emerald',
    stats: '50+ metrics',
  },
  {
    title: 'Portfolio',
    description: 'Track holdings, monitor tier allocation, get deployment recommendations',
    icon: Briefcase,
    path: '/portfolio',
    gradient: 'from-violet-500 to-purple-400',
    accent: 'violet',
    stats: '3-tier system',
  },
]

const features = [
  {
    icon: Sparkles,
    label: 'AI-Powered Scoring',
    description: 'Multi-factor composite analysis',
  },
  {
    icon: TrendingUp,
    label: 'Growth Detection',
    description: 'Find compounders early',
  },
  {
    icon: Target,
    label: 'Smart Allocation',
    description: 'Tier-based management',
  },
]

const quickActions = [
  { label: 'Score S&P 500', path: '/universe', icon: BarChart3, primary: true },
  { label: 'Analyze MSFT', path: '/company/MSFT' },
  { label: 'Analyze AAPL', path: '/company/AAPL' },
  { label: 'Analyze NVDA', path: '/company/NVDA' },
  { label: 'View Portfolio', path: '/portfolio', icon: Briefcase },
]

export default function Dashboard() {
  const { data: cacheStats, isLoading: isCacheLoading } = useCacheStats()

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl border border-border/50 bg-card">
        {/* Background effects */}
        <div className="absolute inset-0 bg-grid opacity-50" />
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/4" />
        <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-violet-500/10 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/4" />

        <div className="relative p-8 md:p-12">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6">
            <Zap className="h-3.5 w-3.5" />
            Professional Stock Analysis
          </div>

          {/* Heading */}
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Find Quality{' '}
            <span className="gradient-text">Compounders</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed mb-8">
            Before they become mega-caps. Systematic screening, scoring, and portfolio management for the sophisticated investor.
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-3">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div
                  key={feature.label}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-accent/50 border border-border/50 backdrop-blur-sm"
                >
                  <div className="p-1.5 rounded-lg bg-primary/10">
                    <Icon className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <span className="text-sm font-medium block leading-tight">{feature.label}</span>
                    <span className="text-xs text-muted-foreground">{feature.description}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Navigation Cards */}
      <section>
        <div className="flex items-center gap-2 mb-5">
          <h2 className="text-lg font-semibold">Get Started</h2>
          <div className="h-px flex-1 bg-border/50" />
        </div>

        <div className="grid gap-5 md:grid-cols-3">
          {navigationCards.map((card) => {
            const Icon = card.icon
            return (
              <Link key={card.path} to={card.path} className="group">
                <Card className="h-full transition-all duration-300 hover:shadow-xl hover:shadow-primary/5 hover:-translate-y-1">
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`p-3 rounded-xl bg-gradient-to-br ${card.gradient} shadow-lg`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <ArrowRight className="h-5 w-5 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-200" />
                    </div>
                    <CardTitle className="text-xl mb-1">{card.title}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {card.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="inline-flex items-center px-2.5 py-1 rounded-md bg-accent text-xs font-medium text-muted-foreground">
                      {card.stats}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            )
          })}
        </div>
      </section>

      {/* Two column layout */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* System Status */}
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-primary/10">
                <Database className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-base">System Status</CardTitle>
                <CardDescription>Data cache and API health</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isCacheLoading ? (
              <div className="grid gap-4 grid-cols-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <div className="h-3 bg-accent rounded w-16 animate-pulse" />
                    <div className="h-8 bg-accent rounded w-12 animate-pulse" />
                  </div>
                ))}
              </div>
            ) : cacheStats ? (
              <div className="grid gap-6 grid-cols-2">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Database className="h-3.5 w-3.5" />
                    Cached Items
                  </div>
                  <p className="text-2xl font-bold font-mono">{cacheStats.valid_count}</p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <HardDrive className="h-3.5 w-3.5" />
                    Cache Size
                  </div>
                  <p className="text-2xl font-bold font-mono">
                    {cacheStats.total_size_mb.toFixed(1)}
                    <span className="text-sm font-normal text-muted-foreground ml-1">MB</span>
                  </p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="h-3.5 w-3.5" />
                    Cache TTL
                  </div>
                  <p className="text-2xl font-bold font-mono">
                    {cacheStats.ttl_hours}
                    <span className="text-sm font-normal text-muted-foreground ml-1">hrs</span>
                  </p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <AlertCircle className="h-3.5 w-3.5" />
                    Expired
                  </div>
                  <p className="text-2xl font-bold font-mono">{cacheStats.expired_count}</p>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-muted-foreground py-4">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm">Connect to API to view cache stats</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-primary/10">
                <LineChart className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-base">Quick Actions</CardTitle>
                <CardDescription>Jump to common tasks</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action) => {
                const Icon = action.icon
                return (
                  <Link
                    key={action.path + action.label}
                    to={action.path}
                    className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all duration-200 text-sm ${
                      action.primary
                        ? 'bg-primary/10 hover:bg-primary/15 text-primary border border-primary/20'
                        : 'bg-accent hover:bg-accent/80 border border-border text-foreground'
                    }`}
                  >
                    {Icon && <Icon className="h-4 w-4" />}
                    {action.label}
                  </Link>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom info cards */}
      <section className="grid gap-4 md:grid-cols-3">
        <div className="flex items-center gap-4 p-4 rounded-xl bg-accent/30 border border-border/50">
          <div className="p-2.5 rounded-lg bg-success/10">
            <Shield className="h-5 w-5 text-success" />
          </div>
          <div>
            <p className="text-sm font-medium">Data Protected</p>
            <p className="text-xs text-muted-foreground">Local caching enabled</p>
          </div>
        </div>
        <div className="flex items-center gap-4 p-4 rounded-xl bg-accent/30 border border-border/50">
          <div className="p-2.5 rounded-lg bg-primary/10">
            <Zap className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium">Fast Analysis</p>
            <p className="text-xs text-muted-foreground">Cached data loads instantly</p>
          </div>
        </div>
        <div className="flex items-center gap-4 p-4 rounded-xl bg-accent/30 border border-border/50">
          <div className="p-2.5 rounded-lg bg-violet-500/10">
            <Target className="h-5 w-5 text-violet-400" />
          </div>
          <div>
            <p className="text-sm font-medium">Tier Allocation</p>
            <p className="text-xs text-muted-foreground">Smart portfolio management</p>
          </div>
        </div>
      </section>
    </div>
  )
}
