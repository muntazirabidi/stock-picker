import { useMemo } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import type { TierAllocation } from '@/types'

interface AllocationChartProps {
  data: TierAllocation[]
  height?: number
}

const TIER_CONFIG = {
  tier_1: {
    label: 'Tier 1',
    sublabel: 'Established',
    color: '#6366f1',
    gradient: ['#6366f1', '#8b5cf6'],
  },
  tier_2: {
    label: 'Tier 2',
    sublabel: 'Growth',
    color: '#22c55e',
    gradient: ['#22c55e', '#10b981'],
  },
  tier_3: {
    label: 'Tier 3',
    sublabel: 'Opportunistic',
    color: '#f59e0b',
    gradient: ['#f59e0b', '#f97316'],
  },
}

export function AllocationChart({ data, height = 300 }: AllocationChartProps) {
  const chartData = useMemo(() => {
    return data.map((tier) => {
      const config = TIER_CONFIG[tier.tier as keyof typeof TIER_CONFIG] || {
        label: tier.tier,
        sublabel: '',
        color: '#64748b',
        gradient: ['#64748b', '#475569'],
      }
      return {
        name: config.label,
        sublabel: config.sublabel,
        value: tier.actual_pct * 100,
        target: tier.target_pct * 100,
        actualValue: tier.actual_value,
        positions: tier.num_positions,
        color: config.color,
        gradient: config.gradient,
        tier: tier.tier,
      }
    })
  }, [data])

  const totalValue = useMemo(() => {
    return data.reduce((sum, tier) => sum + tier.actual_value, 0)
  }, [data])

  return (
    <div className="relative" style={{ height }}>
      {/* Center total display */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
        <div className="text-center">
          <div className="text-2xl font-bold text-white font-mono">
            ${(totalValue / 1000).toFixed(1)}k
          </div>
          <div className="text-[10px] uppercase tracking-wider text-slate-500 font-medium">
            Total Value
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <defs>
            {chartData.map((entry, index) => (
              <linearGradient
                key={`gradient-${index}`}
                id={`pieGradient-${index}`}
                x1="0"
                y1="0"
                x2="1"
                y2="1"
              >
                <stop offset="0%" stopColor={entry.gradient[0]} stopOpacity={1} />
                <stop offset="100%" stopColor={entry.gradient[1]} stopOpacity={0.8} />
              </linearGradient>
            ))}
            <filter id="pieShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="4" floodOpacity="0.3"/>
            </filter>
          </defs>

          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={65}
            outerRadius={95}
            paddingAngle={3}
            dataKey="value"
            nameKey="name"
            strokeWidth={0}
            filter="url(#pieShadow)"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={`url(#pieGradient-${index})`}
                stroke={entry.color}
                strokeWidth={2}
                strokeOpacity={0.3}
              />
            ))}
          </Pie>

          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload
                const variance = d.value - d.target
                return (
                  <div className="bg-slate-900/95 backdrop-blur-sm border border-slate-700/50 rounded-xl shadow-2xl p-4 min-w-[180px]">
                    <div className="flex items-center gap-2 mb-3">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: d.color }}
                      />
                      <div>
                        <p className="font-semibold text-white">{d.name}</p>
                        <p className="text-xs text-slate-500">{d.sublabel}</p>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-400">Actual</span>
                        <span className="text-sm font-semibold text-white">{d.value.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-400">Target</span>
                        <span className="text-sm text-slate-300">{d.target.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-400">Variance</span>
                        <span className={`text-sm font-medium ${variance >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {variance >= 0 ? '+' : ''}{variance.toFixed(1)}%
                        </span>
                      </div>
                      <div className="pt-2 mt-2 border-t border-slate-700/50 flex justify-between items-center">
                        <span className="text-sm text-slate-400">Positions</span>
                        <span className="text-sm font-medium text-white">{d.positions}</span>
                      </div>
                    </div>
                  </div>
                )
              }
              return null
            }}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Custom legend */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-center gap-6">
        {chartData.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full shadow-lg"
              style={{
                backgroundColor: entry.color,
                boxShadow: `0 0 8px ${entry.color}40`,
              }}
            />
            <div className="text-xs">
              <span className="text-slate-300 font-medium">{entry.name}</span>
              <span className="text-slate-500 ml-1">({entry.value.toFixed(0)}%)</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
