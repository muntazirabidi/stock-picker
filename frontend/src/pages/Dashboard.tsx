import { Link } from 'react-router-dom'
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
} from 'lucide-react'

const navigationCards = [
  {
    title: 'Universe',
    description: 'Score and rank stocks across S&P 500, Nasdaq 100, and custom lists',
    icon: BarChart3,
    path: '/universe',
    illustration: '/illustrations/undraw_space-exploration_dhu1.svg',
    stats: '500+ stocks',
    gradientBg: 'from-cyan-500/20 via-indigo-500/10 to-transparent',
    glowColor: 'bg-cyan-500/30',
  },
  {
    title: 'Company Analysis',
    description: 'Deep fundamental analysis with quality, growth & valuation metrics',
    icon: Building2,
    path: '/company',
    illustration: '/illustrations/undraw_all-the-data_ijgn.svg',
    stats: '50+ metrics',
    gradientBg: 'from-emerald-500/20 via-teal-500/10 to-transparent',
    glowColor: 'bg-emerald-500/30',
  },
  {
    title: 'Portfolio',
    description: 'Track holdings, monitor tier allocation, get deployment recommendations',
    icon: Briefcase,
    path: '/portfolio',
    illustration: '/illustrations/undraw_stock-prices_8nuz.svg',
    stats: '3-tier system',
    gradientBg: 'from-violet-500/20 via-purple-500/10 to-transparent',
    glowColor: 'bg-violet-500/30',
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
      <section className="relative overflow-hidden rounded-2xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0f0f14]">
        {/* Background effects */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.1),transparent_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(139,92,246,0.08),transparent_60%)]" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[1px] bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent" />

        <div className="relative p-8 md:p-10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-10">
            {/* Left content */}
            <div className="flex-1 max-w-lg">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/[0.08] border border-indigo-500/20 text-indigo-400 text-[11px] font-medium mb-6 backdrop-blur-sm">
                <Zap className="h-3 w-3" />
                Professional Stock Analysis
              </div>

              {/* Heading */}
              <h1 className="text-3xl md:text-[40px] font-bold tracking-tight text-white mb-4 leading-[1.1]">
                Find Quality{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400">Compounders</span>
              </h1>
              <p className="text-[15px] text-zinc-400 leading-relaxed mb-8">
                Before they become mega-caps. Systematic screening, scoring, and portfolio management for the sophisticated investor.
              </p>

              {/* Feature pills */}
              <div className="flex flex-wrap gap-2.5">
                {features.map((feature) => {
                  const Icon = feature.icon
                  return (
                    <div
                      key={feature.label}
                      className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-white/[0.03] border border-white/[0.06] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.1] transition-colors"
                    >
                      <Icon className="h-3.5 w-3.5 text-indigo-400" />
                      <span className="text-[12px] font-medium text-zinc-300">{feature.label}</span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Right illustration */}
            <div className="hidden lg:flex flex-shrink-0 relative items-center justify-center">
              <div className="absolute w-64 h-64 bg-indigo-500/15 blur-[80px] rounded-full" />
              <div className="absolute w-48 h-48 bg-violet-500/10 blur-[60px] rounded-full translate-x-8 translate-y-4" />
              <img
                src="/illustrations/undraw_investing_uzcu.svg"
                alt="Investing illustration"
                className="relative w-[280px] h-auto drop-shadow-2xl"
                style={{ filter: 'saturate(1.1) brightness(1.05)' }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Navigation Cards with Illustrations */}
      <section>
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-[15px] font-semibold text-white">Get Started</h2>
          <div className="h-px flex-1 bg-white/[0.06]" />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {navigationCards.map((card) => {
            const Icon = card.icon
            return (
              <Link key={card.path} to={card.path} className="group">
                <div className="relative h-full rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0a0a0d] overflow-hidden transition-all duration-300 hover:border-white/[0.08] hover:shadow-2xl hover:shadow-indigo-500/5">
                  {/* Illustration area */}
                  <div className="relative h-44 flex items-center justify-center overflow-hidden">
                    {/* Gradient background */}
                    <div className={`absolute inset-0 bg-gradient-to-b ${card.gradientBg}`} />
                    {/* Glow effect */}
                    <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 ${card.glowColor} blur-[60px] rounded-full opacity-40 group-hover:opacity-60 transition-opacity duration-500`} />
                    {/* Bottom fade */}
                    <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#0a0a0d] to-transparent" />
                    <img
                      src={card.illustration}
                      alt={card.title}
                      className="relative h-36 w-auto object-contain drop-shadow-2xl group-hover:scale-105 transition-transform duration-500 ease-out"
                      style={{ filter: 'saturate(1.1) brightness(1.05)' }}
                    />
                  </div>

                  {/* Content */}
                  <div className="relative px-5 pb-5">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-[15px] font-semibold text-white">{card.title}</h3>
                      <ArrowRight className="h-4 w-4 text-zinc-600 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all duration-300" />
                    </div>
                    <p className="text-[12px] text-zinc-500 leading-relaxed mb-3">
                      {card.description}
                    </p>
                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.05]">
                      <Icon className="h-3 w-3 text-zinc-500" />
                      <span className="text-[10px] font-medium text-zinc-500">{card.stats}</span>
                    </div>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      {/* Two column layout */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* System Status */}
        <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/10">
              <Database className="h-4 w-4 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-[13px] font-semibold text-white">System Status</h3>
              <p className="text-[11px] text-zinc-500">Data cache and API health</p>
            </div>
          </div>

          {isCacheLoading ? (
            <div className="grid gap-4 grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <div className="h-3 bg-white/[0.04] rounded w-16 animate-pulse" />
                  <div className="h-7 bg-white/[0.04] rounded w-12 animate-pulse" />
                </div>
              ))}
            </div>
          ) : cacheStats ? (
            <div className="grid gap-x-8 gap-y-5 grid-cols-2">
              <div>
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1.5">Cached Items</p>
                <p className="text-2xl font-semibold font-mono text-white">{cacheStats.valid_count}</p>
              </div>
              <div>
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1.5">Cache Size</p>
                <p className="text-2xl font-semibold font-mono text-white">
                  {cacheStats.total_size_mb.toFixed(1)}
                  <span className="text-sm font-normal text-zinc-500 ml-1">MB</span>
                </p>
              </div>
              <div>
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1.5">Cache TTL</p>
                <p className="text-2xl font-semibold font-mono text-white">
                  {cacheStats.ttl_hours}
                  <span className="text-sm font-normal text-zinc-500 ml-1">hrs</span>
                </p>
              </div>
              <div>
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1.5">Expired</p>
                <p className="text-2xl font-semibold font-mono text-white">{cacheStats.expired_count}</p>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-zinc-500 py-2">
              <AlertCircle className="h-4 w-4" />
              <span className="text-xs">Connect to API to view cache stats</span>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="rounded-xl border border-white/[0.04] bg-gradient-to-br from-[#0c0c0f] to-[#0e0e12] p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/10">
              <Zap className="h-4 w-4 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-[13px] font-semibold text-white">Quick Actions</h3>
              <p className="text-[11px] text-zinc-500">Jump to common tasks</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2.5">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <Link
                  key={action.path + action.label}
                  to={action.path}
                  className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-[12px] font-medium transition-all duration-150 ${
                    action.primary
                      ? 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/20 hover:border-indigo-500/30'
                      : 'bg-white/[0.02] hover:bg-white/[0.05] border border-white/[0.06] hover:border-white/[0.1] text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  {Icon && <Icon className="h-3.5 w-3.5" />}
                  {action.label}
                </Link>
              )
            })}
          </div>
        </div>
      </div>

    </div>
  )
}
