import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useCacheStats } from '@/hooks/useSystem'
import { BarChart3, Building2, Briefcase, Database, HardDrive, Clock, AlertCircle } from 'lucide-react'

const navigationCards = [
  {
    title: 'Universe',
    description: 'Score and rank stocks from multiple indices',
    icon: BarChart3,
    path: '/universe',
    color: 'text-blue-500',
  },
  {
    title: 'Company',
    description: 'Deep dive analysis of individual stocks',
    icon: Building2,
    path: '/company',
    color: 'text-green-500',
  },
  {
    title: 'Portfolio',
    description: 'Track holdings and allocations',
    icon: Briefcase,
    path: '/portfolio',
    color: 'text-purple-500',
  },
]

export default function Dashboard() {
  const { data: cacheStats, isLoading: isCacheLoading } = useCacheStats()

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-8">
        <h1 className="text-4xl font-light tracking-tight mb-2">
          Equity Research
        </h1>
        <p className="text-lg text-muted-foreground">
          Find quality compounders before they become mega-caps
        </p>
      </div>

      {/* Navigation Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        {navigationCards.map((card) => {
          const Icon = card.icon
          return (
            <Link key={card.path} to={card.path}>
              <Card className="h-full transition-all hover:shadow-lg hover:border-primary/50 cursor-pointer">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-accent ${card.color}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-xl">{card.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {card.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-medium flex items-center gap-2">
            <Database className="h-5 w-5" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isCacheLoading ? (
            <div className="grid gap-4 md:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-muted rounded w-20 mb-2" />
                  <div className="h-8 bg-muted rounded w-16" />
                </div>
              ))}
            </div>
          ) : cacheStats ? (
            <div className="grid gap-4 md:grid-cols-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Database className="h-4 w-4" />
                  Cached
                </p>
                <p className="text-2xl font-semibold">{cacheStats.valid_count}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <HardDrive className="h-4 w-4" />
                  Size
                </p>
                <p className="text-2xl font-semibold">{cacheStats.total_size_mb.toFixed(1)} MB</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  TTL
                </p>
                <p className="text-2xl font-semibold">{cacheStats.ttl_hours}h</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  Expired
                </p>
                <p className="text-2xl font-semibold">{cacheStats.expired_count}</p>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">Unable to load cache stats</p>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-medium">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Link to="/universe">
              <Badge variant="secondary" className="cursor-pointer hover:bg-accent/80 px-3 py-1.5">
                Score S&P 500
              </Badge>
            </Link>
            <Link to="/company/MSFT">
              <Badge variant="secondary" className="cursor-pointer hover:bg-accent/80 px-3 py-1.5">
                Analyze MSFT
              </Badge>
            </Link>
            <Link to="/company/AAPL">
              <Badge variant="secondary" className="cursor-pointer hover:bg-accent/80 px-3 py-1.5">
                Analyze AAPL
              </Badge>
            </Link>
            <Link to="/portfolio">
              <Badge variant="secondary" className="cursor-pointer hover:bg-accent/80 px-3 py-1.5">
                View Portfolio
              </Badge>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
