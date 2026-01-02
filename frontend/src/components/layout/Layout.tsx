import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { BarChart3, Building2, Briefcase, Home } from 'lucide-react'

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
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 max-w-screen-2xl items-center">
          <Link to="/" className="flex items-center space-x-2 mr-6">
            <BarChart3 className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">Equity Research</span>
          </Link>

          <nav className="flex items-center space-x-6 text-sm font-medium">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path ||
                (item.path !== '/' && location.pathname.startsWith(item.path))
              const Icon = item.icon

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center gap-2 transition-colors hover:text-foreground/80',
                    isActive ? 'text-foreground' : 'text-foreground/60'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container max-w-screen-2xl py-6">
        {children}
      </main>
    </div>
  )
}
