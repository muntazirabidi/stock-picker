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
  Target
} from 'lucide-react'

const navigationCards = [
  {
    title: 'Universe',
    description: 'Score and rank stocks across S&P 500, Nasdaq 100, and more',
    icon: BarChart3,
    path: '/universe',
    gradient: 'from-blue-500 to-cyan-500',
    stats: '500+ stocks',
  },
  {
    title: 'Company',
    description: 'Deep fundamental analysis with quality, growth & valuation metrics',
    icon: Building2,
    path: '/company',
    gradient: 'from-emerald-500 to-teal-500',
    stats: '6 metrics tabs',
  },
  {
    title: 'Portfolio',
    description: 'Track holdings, tier allocation, and deployment recommendations',
    icon: Briefcase,
    path: '/portfolio',
    gradient: 'from-violet-500 to-purple-500',
    stats: '3-tier system',
  },
]

const features = [
  { icon: Sparkles, label: 'AI-Powered Scoring', description: 'Multi-factor composite scores' },
  { icon: TrendingUp, label: 'Growth Detection', description: 'Find compounders early' },
  { icon: Target, label: 'Smart Allocation', description: 'Tier-based portfolio management' },
]

export default function Dashboard() {
  const { data: cacheStats, isLoading: isCacheLoading } = useCacheStats()

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-card via-card to-primary/5 border border-border/50 p-10">
        <div className="absolute inset-0 bg-grid-white/[0.02]" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-4">
            <Sparkles className="h-4 w-4" />
            Professional Stock Analysis
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Find Quality <span className="gradient-text">Compounders</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            Before they become mega-caps. Systematic screening, scoring, and portfolio management for the sophisticated investor.
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-3 mt-8">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div
                  key={feature.label}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent/50 border border-border/50"
                >
                  <Icon className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium">{feature.label}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Navigation Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        {navigationCards.map((card) => {
          const Icon = card.icon
          return (
            <Link key={card.path} to={card.path} className="group">
              <Card className="h-full transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5 hover:border-primary/30 hover:-translate-y-1 bg-card/50 backdrop-blur">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-3">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${card.gradient} shadow-lg`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                  </div>
                  <CardTitle className="text-xl">{card.title}</CardTitle>
                  <CardDescription className="text-base">
                    {card.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="inline-flex items-center px-2.5 py-1 rounded-md bg-accent/50 text-xs font-medium text-muted-foreground">
                    {card.stats}
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* System Status */}
      <Card className="bg-card/50 backdrop-blur border-border/50">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent">
              <Database className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg font-semibold">System Status</CardTitle>
              <CardDescription>Data cache and API health</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isCacheLoading ? (
            <div className="grid gap-6 md:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-accent rounded w-20 mb-2" />
                  <div className="h-8 bg-accent rounded w-16" />
                </div>
              ))}
            </div>
          ) : cacheStats ? (
            <div className="grid gap-6 md:grid-cols-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Database className="h-4 w-4" />
                  Cached Items
                </div>
                <p className="text-3xl font-bold">{cacheStats.valid_count}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <HardDrive className="h-4 w-4" />
                  Cache Size
                </div>
                <p className="text-3xl font-bold">{cacheStats.total_size_mb.toFixed(1)}<span className="text-lg font-normal text-muted-foreground ml-1">MB</span></p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  TTL
                </div>
                <p className="text-3xl font-bold">{cacheStats.ttl_hours}<span className="text-lg font-normal text-muted-foreground ml-1">hrs</span></p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <AlertCircle className="h-4 w-4" />
                  Expired
                </div>
                <p className="text-3xl font-bold">{cacheStats.expired_count}</p>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-muted-foreground">
              <AlertCircle className="h-4 w-4" />
              <span>Connect to API to view cache stats</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card className="bg-card/50 backdrop-blur border-border/50">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold">Quick Actions</CardTitle>
          <CardDescription>Jump to common tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/universe"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary/10 hover:bg-primary/20 border border-primary/20 text-primary font-medium transition-colors"
            >
              <BarChart3 className="h-4 w-4" />
              Score S&P 500
            </Link>
            <Link
              to="/company/MSFT"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent hover:bg-accent/80 border border-border font-medium transition-colors"
            >
              Analyze MSFT
            </Link>
            <Link
              to="/company/AAPL"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent hover:bg-accent/80 border border-border font-medium transition-colors"
            >
              Analyze AAPL
            </Link>
            <Link
              to="/company/NVDA"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent hover:bg-accent/80 border border-border font-medium transition-colors"
            >
              Analyze NVDA
            </Link>
            <Link
              to="/portfolio"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent hover:bg-accent/80 border border-border font-medium transition-colors"
            >
              <Briefcase className="h-4 w-4" />
              View Portfolio
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
