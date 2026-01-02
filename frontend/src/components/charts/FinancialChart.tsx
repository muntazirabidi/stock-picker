import { useMemo } from 'react'
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import type { IncomeStatement } from '@/types'

interface FinancialChartProps {
  data: IncomeStatement[]
  height?: number
}

export function FinancialChart({ data, height = 300 }: FinancialChartProps) {
  const chartData = useMemo(() => {
    return [...data]
      .reverse()
      .map((stmt) => ({
        year: new Date(stmt.date).getFullYear().toString(),
        revenue: stmt.revenue / 1e9,
        netIncome: stmt.net_income / 1e9,
      }))
  }, [data])

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
        <XAxis
          dataKey="year"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#6b7280', fontSize: 12 }}
        />
        <YAxis
          yAxisId="left"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#6b7280', fontSize: 12 }}
          tickFormatter={(value) => `$${value.toFixed(0)}B`}
          width={60}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#6b7280', fontSize: 12 }}
          tickFormatter={(value) => `$${value.toFixed(0)}B`}
          width={60}
        />
        <Tooltip
          content={({ active, payload, label }) => {
            if (active && payload && payload.length) {
              return (
                <div className="bg-card border rounded-lg shadow-lg p-3">
                  <p className="text-sm font-medium mb-2">{label}</p>
                  {payload.map((entry) => (
                    <p key={entry.dataKey} className="text-sm" style={{ color: entry.color }}>
                      {entry.name}: ${(entry.value as number).toFixed(2)}B
                    </p>
                  ))}
                </div>
              )
            }
            return null
          }}
        />
        <Legend />
        <Bar
          yAxisId="left"
          dataKey="revenue"
          name="Revenue"
          fill="#1565c0"
          radius={[4, 4, 0, 0]}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="netIncome"
          name="Net Income"
          stroke="#2e7d32"
          strokeWidth={2}
          dot={{ fill: '#2e7d32', r: 4 }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
