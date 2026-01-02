import { useMemo } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import type { TierAllocation } from '@/types'

interface AllocationChartProps {
  data: TierAllocation[]
  height?: number
}

const COLORS = ['#1565c0', '#2e7d32', '#ef6c00']
const TIER_LABELS: Record<string, string> = {
  tier_1: 'Tier 1 (Established)',
  tier_2: 'Tier 2 (Growth)',
  tier_3: 'Tier 3 (Opportunistic)',
}

export function AllocationChart({ data, height = 300 }: AllocationChartProps) {
  const chartData = useMemo(() => {
    return data.map((tier, index) => ({
      name: TIER_LABELS[tier.tier] || tier.tier,
      value: tier.actual_pct * 100,
      target: tier.target_pct * 100,
      actualValue: tier.actual_value,
      positions: tier.num_positions,
      color: COLORS[index % COLORS.length],
    }))
  }, [data])

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
          nameKey="name"
          label={({ value }) => `${value.toFixed(0)}%`}
          labelLine={false}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload
              return (
                <div className="bg-card border rounded-lg shadow-lg p-3">
                  <p className="font-medium">{data.name}</p>
                  <p className="text-sm text-muted-foreground">
                    Actual: {data.value.toFixed(1)}%
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Target: {data.target.toFixed(1)}%
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Positions: {data.positions}
                  </p>
                </div>
              )
            }
            return null
          }}
        />
        <Legend
          verticalAlign="bottom"
          height={36}
          formatter={(value) => <span className="text-sm">{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
