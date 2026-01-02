import { useMemo } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { PriceBar } from '@/types'

interface PriceChartProps {
  data: PriceBar[]
  height?: number
}

export function PriceChart({ data, height = 300 }: PriceChartProps) {
  const chartData = useMemo(() => {
    return data.map((bar) => ({
      date: new Date(bar.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
      fullDate: bar.date,
      price: bar.close,
      volume: bar.volume,
    }))
  }, [data])

  const isPositive = useMemo(() => {
    if (data.length < 2) return true
    return data[data.length - 1].close >= data[0].close
  }, [data])

  const minPrice = useMemo(() => {
    return Math.min(...data.map((d) => d.close)) * 0.98
  }, [data])

  const maxPrice = useMemo(() => {
    return Math.max(...data.map((d) => d.close)) * 1.02
  }, [data])

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="5%"
              stopColor={isPositive ? '#2e7d32' : '#c62828'}
              stopOpacity={0.3}
            />
            <stop
              offset="95%"
              stopColor={isPositive ? '#2e7d32' : '#c62828'}
              stopOpacity={0}
            />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#6b7280', fontSize: 12 }}
          interval="preserveStartEnd"
        />
        <YAxis
          domain={[minPrice, maxPrice]}
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#6b7280', fontSize: 12 }}
          tickFormatter={(value) => `$${value.toFixed(0)}`}
          width={60}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload
              return (
                <div className="bg-card border rounded-lg shadow-lg p-3">
                  <p className="text-sm text-muted-foreground">{data.fullDate}</p>
                  <p className="text-lg font-semibold">${data.price.toFixed(2)}</p>
                </div>
              )
            }
            return null
          }}
        />
        <Area
          type="monotone"
          dataKey="price"
          stroke={isPositive ? '#2e7d32' : '#c62828'}
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorPrice)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
