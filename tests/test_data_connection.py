"""Test data connection using Yahoo Finance (free)."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import YahooClient


def test_yahoo_connection():
    """Test Yahoo Finance data connectivity."""
    print("Testing Yahoo Finance connection...")
    print("(Using free yfinance library - no API key needed)\n")

    client = YahooClient()

    # Test 1: Get a quote
    print("1. Testing quote (AAPL)...")
    quote = client.get_quote("AAPL")
    if quote:
        print(f"   ✓ AAPL price: ${quote.price:.2f}")
        print(f"     Market Cap: ${quote.market_cap/1e12:.2f}T")
    else:
        print("   ✗ Failed to get quote")
        return False

    # Test 2: Get a profile
    print("\n2. Testing profile (MSFT)...")
    profile = client.get_profile("MSFT")
    if profile:
        print(f"   ✓ {profile.company_name}")
        print(f"     Sector: {profile.sector}")
        print(f"     Market Cap: ${profile.market_cap/1e12:.2f}T")
    else:
        print("   ✗ Failed to get profile")
        return False

    # Test 3: Get S&P 500 tickers
    print("\n3. Testing S&P 500 ticker list...")
    sp500 = client.get_sp500_tickers()
    if sp500:
        print(f"   ✓ Found {len(sp500)} S&P 500 stocks")
        print(f"     First 5: {sp500[:5]}")
    else:
        print("   ✗ Failed to get S&P 500 list")
        return False

    # Test 4: Get income statements
    print("\n4. Testing income statements (COST)...")
    income = client.get_income_statements("COST", limit=5)
    if income:
        latest = income[0]
        print(f"   ✓ Latest revenue: ${latest.revenue/1e9:.1f}B ({latest.date})")
        print(f"     Gross margin: {latest.gross_profit_ratio*100:.1f}%")
        print(f"     Net margin: {latest.net_income_ratio*100:.1f}%")
        print(f"     Years of data: {len(income)}")
    else:
        print("   ✗ Failed to get income statements")
        return False

    # Test 5: Get balance sheet
    print("\n5. Testing balance sheet (NVDA)...")
    balance = client.get_balance_sheets("NVDA", limit=3)
    if balance:
        latest = balance[0]
        print(f"   ✓ Total Assets: ${latest.total_assets/1e9:.1f}B ({latest.date})")
        if latest.cash_and_equivalents:
            print(f"     Cash: ${latest.cash_and_equivalents/1e9:.1f}B")
        if latest.total_equity:
            print(f"     Equity: ${latest.total_equity/1e9:.1f}B")
    else:
        print("   ✗ Failed to get balance sheet")
        return False

    # Test 6: Get cash flow
    print("\n6. Testing cash flow statement (GOOGL)...")
    cashflow = client.get_cash_flow_statements("GOOGL", limit=3)
    if cashflow:
        latest = cashflow[0]
        if latest.operating_cash_flow:
            print(f"   ✓ Operating CF: ${latest.operating_cash_flow/1e9:.1f}B ({latest.date})")
        if latest.free_cash_flow:
            print(f"     Free Cash Flow: ${latest.free_cash_flow/1e9:.1f}B")
        if latest.stock_based_compensation:
            print(f"     Stock-Based Comp: ${latest.stock_based_compensation/1e9:.1f}B")
    else:
        print("   ✗ Failed to get cash flow")
        return False

    # Test 7: Full company financials
    print("\n7. Testing full company fetch (HUBS)...")
    financials = client.get_company_financials("HUBS", years=5)
    if financials:
        print(f"   ✓ {financials.profile.company_name}")
        print(f"     Sector: {financials.profile.sector}")
        print(f"     Income statements: {len(financials.income_statements)} years")
        print(f"     Balance sheets: {len(financials.balance_sheets)} years")
        print(f"     Cash flows: {len(financials.cash_flows)} years")
        if financials.quote:
            print(f"     Current price: ${financials.quote.price:.2f}")
    else:
        print("   ✗ Failed to get company financials")
        return False

    # Test 8: Key metrics
    print("\n8. Testing key metrics (FICO)...")
    metrics = client.get_key_metrics("FICO")
    if metrics:
        m = metrics[0]
        print(f"   ✓ P/E Ratio: {m.pe_ratio:.1f}" if m.pe_ratio else "   ✓ P/E: N/A")
        print(f"     P/S Ratio: {m.price_to_sales:.1f}" if m.price_to_sales else "     P/S: N/A")
        print(f"     P/B Ratio: {m.price_to_book:.1f}" if m.price_to_book else "     P/B: N/A")
        print(f"     ROE: {m.roe*100:.1f}%" if m.roe else "     ROE: N/A")
    else:
        print("   ✗ Failed to get key metrics")

    # Cache stats
    print("\n9. Cache statistics...")
    stats = client.cache_stats()
    print(f"   Total cached: {stats['valid']} entries")
    print(f"   Cache size: {stats['total_size_mb']} MB")

    print("\n" + "="*50)
    print("All tests passed! Yahoo Finance working.")
    print("="*50)

    return True


if __name__ == "__main__":
    success = test_yahoo_connection()
    sys.exit(0 if success else 1)
