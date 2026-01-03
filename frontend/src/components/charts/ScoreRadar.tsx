import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

interface ScoreRadarProps {
  quality: number
  growth: number
  strength: number
  valuation: number
  size?: number
}

export function ScoreRadar({ quality, growth, strength, valuation, size = 250 }: ScoreRadarProps) {
  const data = [
    { metric: 'Quality', score: quality, fullMark: 100 },
    { metric: 'Growth', score: growth, fullMark: 100 },
    { metric: 'Strength', score: strength, fullMark: 100 },
    { metric: 'Valuation', score: valuation, fullMark: 100 },
  ]

  const avgScore = (quality + growth + strength + valuation) / 4

  // Determine color based on average score
  const getColors = (score: number) => {
    if (score >= 70) return { stroke: '#22c55e', fill: '#22c55e', bg: 'rgba(34, 197, 94, 0.15)' }
    if (score >= 50) return { stroke: '#6366f1', fill: '#6366f1', bg: 'rgba(99, 102, 241, 0.15)' }
    return { stroke: '#f59e0b', fill: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)' }
  }

  const colors = getColors(avgScore)

  return (
    <div style={{ width: size, height: size }} className="relative">
      {/* Center score display */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
        <div className="text-center">
          <div className="text-3xl font-bold" style={{ color: colors.stroke }}>
            {avgScore.toFixed(0)}
          </div>
          <div className="text-[10px] uppercase tracking-wider text-slate-500 font-medium">
            Avg Score
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="65%" data={data}>
          <defs>
            <linearGradient id="radarGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={colors.fill} stopOpacity={0.4} />
              <stop offset="100%" stopColor={colors.fill} stopOpacity={0.1} />
            </linearGradient>
            <filter id="radarGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          <PolarGrid
            stroke="#334155"
            strokeOpacity={0.6}
            gridType="polygon"
          />
          <PolarAngleAxis
            dataKey="metric"
            tick={{
              fill: '#94a3b8',
              fontSize: 11,
              fontWeight: 500,
            }}
            tickLine={false}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#475569', fontSize: 9 }}
            tickCount={5}
            axisLine={false}
          />

          <Radar
            name="Score"
            dataKey="score"
            stroke={colors.stroke}
            fill="url(#radarGradient)"
            strokeWidth={2.5}
            filter="url(#radarGlow)"
            dot={{
              fill: colors.stroke,
              stroke: '#18181b',
              strokeWidth: 2,
              r: 4,
            }}
          />

          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload
                return (
                  <div className="bg-slate-900/95 backdrop-blur-sm border border-slate-700/50 rounded-xl shadow-2xl p-3 min-w-[120px]">
                    <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">{item.metric}</p>
                    <p className="text-2xl font-bold" style={{ color: colors.stroke }}>
                      {item.score.toFixed(0)}
                    </p>
                  </div>
                )
              }
              return null
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
