import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { BarChart3, Building2, Briefcase, Home, TrendingUp, Gem, BookOpen, Activity } from 'lucide-react'

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
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full">
        {/* Subtle gradient line at top */}
        <div className="h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

        <div className="border-b border-border/50 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-16 max-w-screen-2xl items-center">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 mr-10 group">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full group-hover:bg-primary/30 transition-colors" />
                <div className="relative p-2.5 rounded-xl bg-gradient-to-br from-primary to-indigo-600 shadow-lg shadow-primary/20">
                  <TrendingUp className="h-5 w-5 text-white" strokeWidth={2.5} />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-lg tracking-tight leading-none">Equity Research</span>
                <span className="text-[10px] font-medium text-primary tracking-widest uppercase">Pro</span>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center gap-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path ||
                  (item.path !== '/' && location.pathname.startsWith(item.path))
                const Icon = item.icon

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={cn(
                      'relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'text-foreground'
                        : 'text-muted-foreground hover:text-foreground'
                    )}
                  >
                    {/* Active indicator */}
                    {isActive && (
                      <div className="absolute inset-0 bg-accent rounded-lg" />
                    )}
                    <Icon className={cn(
                      'relative h-4 w-4 transition-colors',
                      isActive ? 'text-primary' : ''
                    )} />
                    <span className="relative">{item.label}</span>
                  </Link>
                )
              })}
            </nav>

            {/* Right side */}
            <div className="ml-auto flex items-center gap-4">
              {/* Status indicator */}
              <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-success/10 border border-success/20">
                <div className="status-dot status-online" />
                <span className="text-xs text-success font-medium">Live</span>
              </div>

              {/* Activity indicator */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent border border-border text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                <Activity className="h-4 w-4" />
                <span className="text-xs font-medium">API</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container max-w-screen-2xl py-8">
        <div className="animate-fade-in">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 mt-auto">
        <div className="container max-w-screen-2xl py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <p>Built for sophisticated investors</p>
            <p className="font-mono text-xs">v1.0.0</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
