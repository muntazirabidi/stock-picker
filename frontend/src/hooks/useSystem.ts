import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCacheStats, clearCache } from '@/api/client'

export function useCacheStats() {
  return useQuery({
    queryKey: ['system', 'cache-stats'],
    queryFn: getCacheStats,
    staleTime: 1000 * 60, // 1 minute
  })
}

export function useClearCache() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: clearCache,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system', 'cache-stats'] })
    },
  })
}
