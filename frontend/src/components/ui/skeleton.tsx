import { cn } from '@/lib/utils'

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'rounded-lg bg-accent/50 relative overflow-hidden',
        'after:absolute after:inset-0',
        'after:bg-gradient-to-r after:from-transparent after:via-white/5 after:to-transparent',
        'after:animate-shimmer',
        className
      )}
      {...props}
    />
  )
}

export { Skeleton }
