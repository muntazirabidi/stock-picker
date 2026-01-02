import { useQuery } from '@tanstack/react-query'
import {
  getCompanyProfile,
  getCompanyFinancials,
  getCompanyMetrics,
  getCompanyScore,
  getPriceHistory,
  getTechnicalIndicators,
  getCompanyNews,
} from '@/api/client'

export function useCompanyProfile(ticker: string | undefined) {
  return useQuery({
    queryKey: ['company', ticker, 'profile'],
    queryFn: () => getCompanyProfile(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  })
}

export function useCompanyFinancials(ticker: string | undefined) {
  return useQuery({
    queryKey: ['company', ticker, 'financials'],
    queryFn: () => getCompanyFinancials(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  })
}

export function useCompanyMetrics(ticker: string | undefined) {
  return useQuery({
    queryKey: ['company', ticker, 'metrics'],
    queryFn: () => getCompanyMetrics(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  })
}

export function useCompanyScore(ticker: string | undefined) {
  return useQuery({
    queryKey: ['company', ticker, 'score'],
    queryFn: () => getCompanyScore(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 60, // 1 hour
  })
}

export function usePriceHistory(
  ticker: string | undefined,
  period: '1M' | '1Y' | '2Y' | '5Y' = '1Y'
) {
  return useQuery({
    queryKey: ['company', ticker, 'price', period],
    queryFn: () => getPriceHistory(ticker!, period),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 60, // 1 hour
  })
}

export function useTechnicalIndicators(ticker: string | undefined) {
  return useQuery({
    queryKey: ['company', ticker, 'technical'],
    queryFn: () => getTechnicalIndicators(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 60, // 1 hour
  })
}

export function useCompanyNews(ticker: string | undefined) {
  return useQuery({
    queryKey: ['company', ticker, 'news'],
    queryFn: () => getCompanyNews(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 15, // 15 minutes
  })
}
