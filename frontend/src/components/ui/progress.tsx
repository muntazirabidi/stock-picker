import * as React from 'react'
import { cn } from '@/lib/utils'

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number
  max?: number
  indicatorClassName?: string
  variant?: 'default' | 'success' | 'warning' | 'error' | 'gradient'
  size?: 'sm' | 'default' | 'lg'
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value, max = 100, indicatorClassName, variant = 'default', size = 'default', ...props }, ref) => {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100))

    const sizeClasses = {
      sm: 'h-1',
      default: 'h-2',
      lg: 'h-3',
    }

    const variantClasses = {
      default: 'bg-primary',
      success: 'bg-success',
      warning: 'bg-warning',
      error: 'bg-error',
      gradient: 'bg-gradient-to-r from-primary to-violet-500',
    }

    return (
      <div
        ref={ref}
        className={cn(
          'relative w-full overflow-hidden rounded-full bg-accent/50',
          sizeClasses[size],
          className
        )}
        {...props}
      >
        <div
          className={cn(
            'h-full rounded-full transition-all duration-300 ease-out',
            variantClasses[variant],
            indicatorClassName
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    )
  }
)
Progress.displayName = 'Progress'

export { Progress }
