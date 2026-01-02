import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getUniverseTickers, scoreUniverse, scoreUniverseWithValuation } from '@/api/client'
import type { UniverseType, CompanyScore, CompanyScoreWithValuation } from '@/types'

export function useUniverseTickers(type: UniverseType) {
  return useQuery({
    queryKey: ['universe', 'tickers', type],
    queryFn: () => getUniverseTickers(type),
    staleTime: 1000 * 60 * 60, // 1 hour
  })
}

export function useScoreUniverse() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (tickers: string[]) => scoreUniverse(tickers),
    onSuccess: (data) => {
      queryClient.setQueryData(['universe', 'scores'], data)
    },
  })
}

export function useScoreUniverseWithValuation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (tickers: string[]) => scoreUniverseWithValuation(tickers),
    onSuccess: (data) => {
      queryClient.setQueryData(['universe', 'value-scores'], data)
    },
  })
}

export function useUniverseScores() {
  return useQuery<CompanyScore[]>({
    queryKey: ['universe', 'scores'],
    enabled: false, // Only populated by mutation
  })
}
