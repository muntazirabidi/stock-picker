import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from '@/components/layout/Layout'
import Dashboard from '@/pages/Dashboard'
import Universe from '@/pages/Universe'
import ValuePicks from '@/pages/ValuePicks'
import Company from '@/pages/Company'
import Portfolio from '@/pages/Portfolio'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/universe" element={<Universe />} />
            <Route path="/value-picks" element={<ValuePicks />} />
            <Route path="/company" element={<Company />} />
            <Route path="/company/:ticker" element={<Company />} />
            <Route path="/portfolio" element={<Portfolio />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
