import { useMemo } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
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

  const priceChange = useMemo(() => {
    if (data.length < 2) return { value: 0, percent: 0 }
    const first = data[0].close
    const last = data[data.length - 1].close
    return {
      value: last - first,
      percent: ((last - first) / first) * 100,
    }
  }, [data])

  const colors = {
    positive: {
      stroke: '#22c55e',
      fill: '#22c55e',
      glow: '#22c55e',
    },
    negative: {
      stroke: '#ef4444',
      fill: '#ef4444',
      glow: '#ef4444',
    },
  }

  const theme = isPositive ? colors.positive : colors.negative

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={chartData} margin={{ top: 20, right: 20, left: 10, bottom: 10 }}>
        <defs>
          <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={theme.fill} stopOpacity={0.25} />
            <stop offset="50%" stopColor={theme.fill} stopOpacity={0.1} />
            <stop offset="100%" stopColor={theme.fill} stopOpacity={0} />
          </linearGradient>
          <linearGradient id="strokeGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor={theme.stroke} stopOpacity={0.8} />
            <stop offset="100%" stopColor={theme.stroke} stopOpacity={1} />
          </linearGradient>
          <filter id="priceGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <CartesianGrid
          strokeDasharray="3 6"
          stroke="#27272a"
          vertical={false}
        />

        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#71717a', fontSize: 10 }}
          interval="preserveStartEnd"
          dy={10}
        />
        <YAxis
          domain={[minPrice, maxPrice]}
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#71717a', fontSize: 11 }}
          tickFormatter={(value) => `$${value.toFixed(0)}`}
          width={50}
        />

        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const d = payload[0].payload
              return (
                <div className="bg-slate-900/95 backdrop-blur-sm border border-slate-700/50 rounded-xl shadow-2xl p-4 min-w-[140px]">
                  <p className="text-xs text-slate-500 mb-1">{d.fullDate}</p>
                  <p className="text-2xl font-bold text-white font-mono">${d.price.toFixed(2)}</p>
                  <div className="mt-2 pt-2 border-t border-slate-700/50">
                    <div className="flex items-center gap-1.5">
                      <span className={`text-sm font-medium ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                        {priceChange.value >= 0 ? '+' : ''}{priceChange.value.toFixed(2)}
                      </span>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${isPositive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                        {priceChange.percent >= 0 ? '+' : ''}{priceChange.percent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                </div>
              )
            }
            return null
          }}
          cursor={{
            stroke: theme.stroke,
            strokeWidth: 1,
            strokeDasharray: '4 4',
          }}
        />

        <Area
          type="monotone"
          dataKey="price"
          stroke={theme.stroke}
          strokeWidth={2.5}
          fillOpacity={1}
          fill="url(#priceGradient)"
          filter="url(#priceGlow)"
          dot={false}
          activeDot={{
            fill: theme.stroke,
            stroke: '#18181b',
            strokeWidth: 2,
            r: 6,
          }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
