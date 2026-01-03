import { useMemo } from 'react'
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
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
      <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
        <defs>
          <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" stopOpacity={1} />
            <stop offset="100%" stopColor="#6366f1" stopOpacity={0.7} />
          </linearGradient>
          <linearGradient id="incomeGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#10b981" stopOpacity={1} />
            <stop offset="100%" stopColor="#22c55e" stopOpacity={1} />
          </linearGradient>
          <filter id="barShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#6366f1" floodOpacity="0.3"/>
          </filter>
        </defs>

        <CartesianGrid
          strokeDasharray="3 6"
          stroke="#27272a"
          vertical={false}
        />

        <XAxis
          dataKey="year"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#71717a', fontSize: 11, fontWeight: 500 }}
          dy={10}
        />
        <YAxis
          yAxisId="left"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#71717a', fontSize: 11 }}
          tickFormatter={(value) => `$${value.toFixed(0)}B`}
          width={55}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#71717a', fontSize: 11 }}
          tickFormatter={(value) => `$${value.toFixed(0)}B`}
          width={55}
        />

        <Tooltip
          content={({ active, payload, label }) => {
            if (active && payload && payload.length) {
              return (
                <div className="bg-slate-900/95 backdrop-blur-sm border border-slate-700/50 rounded-xl shadow-2xl p-4 min-w-[160px]">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">{label}</p>
                  {payload.map((entry) => (
                    <div key={entry.dataKey} className="flex items-center justify-between gap-4 py-1">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ backgroundColor: entry.color }}
                        />
                        <span className="text-sm text-slate-300">{entry.name}</span>
                      </div>
                      <span className="text-sm font-semibold text-white">
                        ${(entry.value as number).toFixed(2)}B
                      </span>
                    </div>
                  ))}
                </div>
              )
            }
            return null
          }}
          cursor={{ fill: 'rgba(99, 102, 241, 0.05)' }}
        />

        <Bar
          yAxisId="left"
          dataKey="revenue"
          name="Revenue"
          fill="url(#revenueGradient)"
          radius={[6, 6, 0, 0]}
          barSize={32}
          filter="url(#barShadow)"
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="netIncome"
          name="Net Income"
          stroke="url(#incomeGradient)"
          strokeWidth={3}
          dot={{
            fill: '#10b981',
            stroke: '#18181b',
            strokeWidth: 2,
            r: 5,
          }}
          activeDot={{
            fill: '#10b981',
            stroke: '#fff',
            strokeWidth: 2,
            r: 7,
          }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
