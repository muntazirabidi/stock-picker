import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getPortfolioHoldings,
  getPortfolioAllocation,
  addHolding,
  deleteHolding,
  deployCapital,
} from '@/api/client'
import type { Holding } from '@/types'

export function usePortfolioHoldings() {
  return useQuery({
    queryKey: ['portfolio', 'holdings'],
    queryFn: getPortfolioHoldings,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function usePortfolioAllocation() {
  return useQuery({
    queryKey: ['portfolio', 'allocation'],
    queryFn: getPortfolioAllocation,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function useAddHolding() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (holding: Omit<Holding, 'id'>) => addHolding(holding),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })
}

export function useDeleteHolding() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (ticker: string) => deleteHolding(ticker),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })
}

export function useDeployCapital() {
  return useMutation({
    mutationFn: (amount: number) => deployCapital(amount),
  })
}
