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
  if (score >= 80) return 'text-success'
  if (score >= 60) return 'text-primary'
  if (score >= 40) return 'text-warning'
  return 'text-error'
}

export function getScoreBgColor(score: number): string {
  if (score >= 80) return 'bg-success/10 text-success'
  if (score >= 60) return 'bg-primary/10 text-primary'
  if (score >= 40) return 'bg-warning/10 text-warning'
  return 'bg-error/10 text-error'
}

export function getStageColor(stage: string): string {
  switch (stage.toLowerCase()) {
    case 'compounder':
      return 'bg-success/10 text-success border-success/20'
    case 'growth':
      return 'bg-primary/10 text-primary border-primary/20'
    case 'mature':
      return 'bg-muted/10 text-muted border-muted/20'
    case 'speculative':
      return 'bg-warning/10 text-warning border-warning/20'
    default:
      return 'bg-muted/10 text-muted border-muted/20'
  }
}

export function getChangeColor(value: number): string {
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-error'
  return 'text-muted'
}
