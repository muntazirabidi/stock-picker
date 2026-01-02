"""Quick test to verify FMP API connection works."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import FMPClient, UniverseLoader, get_universe_summary


def test_api_connection():
    """Test basic API connectivity."""
    print("Testing FMP API connection...")

    client = FMPClient()

    # Test 1: Get a quote
    print("\n1. Testing quote endpoint (AAPL)...")
    quote = client.get_quote("AAPL")
    if quote:
        print(f"   ✓ AAPL price: ${quote.price:.2f}")
    else:
        print("   ✗ Failed to get quote")
        return False

    # Test 2: Get a profile
    print("\n2. Testing profile endpoint (MSFT)...")
    profile = client.get_profile("MSFT")
    if profile:
        print(f"   ✓ {profile.company_name}")
        print(f"     Sector: {profile.sector}")
        print(f"     Market Cap: ${profile.market_cap/1e9:.1f}B")
    else:
        print("   ✗ Failed to get profile")
        return False

    # Test 3: Get S&P 500 constituents
    print("\n3. Testing S&P 500 constituents...")
    sp500 = client.get_sp500_constituents()
    print(f"   ✓ Found {len(sp500)} S&P 500 stocks")

    # Test 4: Get financial data
    print("\n4. Testing financial data (COST)...")
    income = client.get_income_statements("COST", limit=3)
    if income:
        latest = income[0]
        print(f"   ✓ Latest revenue: ${latest.revenue/1e9:.1f}B ({latest.date})")
    else:
        print("   ✗ Failed to get income statements")

    # Test 5: Full company financials
    print("\n5. Testing full company fetch (HUBS)...")
    financials = client.get_company_financials("HUBS", years=5)
    if financials:
        print(f"   ✓ {financials.profile.company_name}")
        print(f"     Income statements: {len(financials.income_statements)} years")
        print(f"     Balance sheets: {len(financials.balance_sheets)} years")
        print(f"     Cash flows: {len(financials.cash_flows)} years")
    else:
        print("   ✗ Failed to get company financials")

    # Test 6: Universe loader
    print("\n6. Testing universe loader...")
    loader = UniverseLoader(client)
    universe = loader.load_sp500()
    summary = get_universe_summary(universe)
    print(f"   ✓ Loaded {summary['total']} stocks")
    print(f"     By tier: {summary['by_tier']}")

    # Cache stats
    print("\n7. Cache statistics...")
    stats = client.cache_stats()
    print(f"   Total cached: {stats['valid']} entries")
    print(f"   Cache size: {stats['total_size_mb']} MB")

    print("\n" + "="*50)
    print("All tests passed! API connection working.")
    print("="*50)

    return True


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
