import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatNumber(value: number, decimals = 2): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatPercent(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`
}

export function formatCompactNumber(value: number): string {
  if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`
  if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`
  return `$${value.toFixed(0)}`
}

export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-blue-400'
  if (score >= 40) return 'text-amber-400'
  return 'text-red-400'
}

export function getScoreBgColor(score: number): string {
  if (score >= 80) return 'bg-emerald-500/10 text-emerald-400'
  if (score >= 60) return 'bg-blue-500/10 text-blue-400'
  if (score >= 40) return 'bg-amber-500/10 text-amber-400'
  return 'bg-red-500/10 text-red-400'
}

export function getStageColor(stage: string): string {
  switch (stage.toLowerCase()) {
    case 'compounder':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'growth':
      return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    case 'mature':
      return 'bg-slate-500/10 text-slate-400 border-slate-500/20'
    case 'speculative':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    default:
      return 'bg-slate-500/10 text-slate-400 border-slate-500/20'
  }
}

export function getChangeColor(value: number): string {
  if (value > 0) return 'text-emerald-400'
  if (value < 0) return 'text-red-400'
  return 'text-slate-400'
}
