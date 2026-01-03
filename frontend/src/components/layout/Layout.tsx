import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { BarChart3, Building2, Briefcase, Home, TrendingUp, Gem, BookOpen, Zap, Circle } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/universe', label: 'Universe', icon: BarChart3 },
  { path: '/value-picks', label: 'Value Picks', icon: Gem },
  { path: '/company', label: 'Company', icon: Building2 },
  { path: '/portfolio', label: 'Portfolio', icon: Briefcase },
  { path: '/learning', label: 'Learning', icon: BookOpen },
]

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full">
        <div className="border-b border-white/[0.08] bg-[#0c0c0f]/95 backdrop-blur-2xl">
          <div className="container flex h-14 max-w-screen-2xl items-center px-6">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2.5 mr-8 group">
              <div className="relative flex items-center justify-center w-8 h-8">
                {/* Glow effect */}
                <div className="absolute inset-0 bg-indigo-500/30 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                {/* Icon container */}
                <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600">
                  <TrendingUp className="h-4 w-4 text-white" strokeWidth={2.5} />
                </div>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="font-semibold text-[15px] text-white tracking-tight">Equity Research</span>
                <span className="text-[10px] font-semibold text-indigo-400 tracking-wide uppercase">Pro</span>
              </div>
            </Link>

            {/* Divider */}
            <div className="h-5 w-px bg-white/[0.08] mr-6" />

            {/* Navigation */}
            <nav className="flex items-center gap-0.5">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path ||
                  (item.path !== '/' && location.pathname.startsWith(item.path))
                const Icon = item.icon

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={cn(
                      'relative flex items-center gap-2 px-3.5 py-1.5 rounded-md text-[13px] font-medium transition-all duration-150',
                      isActive
                        ? 'text-white bg-white/[0.08]'
                        : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]'
                    )}
                  >
                    <Icon className={cn(
                      'h-3.5 w-3.5',
                      isActive ? 'text-indigo-400' : ''
                    )} />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </nav>

            {/* Right side */}
            <div className="ml-auto flex items-center gap-3">
              {/* Live status */}
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-emerald-500/20 bg-emerald-500/[0.08]">
                <Circle className="h-2 w-2 fill-emerald-400 text-emerald-400" />
                <span className="text-[11px] text-emerald-400 font-medium tracking-wide">Live</span>
              </div>

              {/* API status */}
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-white/[0.08] bg-white/[0.02] text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04] transition-colors cursor-pointer">
                <Zap className="h-3 w-3" />
                <span className="text-[11px] font-medium tracking-wide">API</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container max-w-screen-2xl py-8 flex-1">
        <div className="animate-fade-in">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.06]">
        <div className="container max-w-screen-2xl py-4 px-6">
          <div className="flex items-center justify-between text-[12px] text-zinc-600">
            <p>Built for sophisticated investors</p>
            <p className="font-mono">v1.0.0</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
