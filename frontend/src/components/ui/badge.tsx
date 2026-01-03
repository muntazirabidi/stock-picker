import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'border-primary/30 bg-primary/10 text-primary',
        secondary: 'border-border bg-accent text-muted-foreground',
        success: 'border-success/30 bg-success/10 text-success',
        warning: 'border-warning/30 bg-warning/10 text-warning',
        error: 'border-error/30 bg-error/10 text-error',
        outline: 'border-border text-muted-foreground bg-transparent',
        solid: 'border-transparent bg-primary text-primary-foreground',
        // Stage variants
        compounder: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
        growth: 'border-blue-500/30 bg-blue-500/10 text-blue-400',
        mature: 'border-violet-500/30 bg-violet-500/10 text-violet-400',
        speculative: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
      },
      size: {
        default: 'px-2 py-0.5 text-xs',
        sm: 'px-1.5 py-0.5 text-[10px]',
        lg: 'px-2.5 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
