import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { BarChart3, Building2, Briefcase, Home, TrendingUp } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/universe', label: 'Universe', icon: BarChart3 },
  { path: '/company', label: 'Company', icon: Building2 },
  { path: '/portfolio', label: 'Portfolio', icon: Briefcase },
]

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="container flex h-16 max-w-screen-2xl items-center px-6">
          <Link to="/" className="flex items-center space-x-3 mr-8">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary to-blue-600 shadow-lg shadow-primary/25">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight">Equity Research</span>
              <span className="text-xs text-muted-foreground block -mt-0.5">Pro</span>
            </div>
          </Link>

          <nav className="flex items-center space-x-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path ||
                (item.path !== '/' && location.pathname.startsWith(item.path))
              const Icon = item.icon

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-primary/10 text-primary shadow-sm'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              )
            })}
          </nav>

          <div className="ml-auto flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/20">
              <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span className="text-xs text-success font-medium">Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container max-w-screen-2xl py-8 px-6">
        {children}
      </main>
    </div>
  )
}
