"""Test portfolio management functionality."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import YahooClient, Tier
from src.metrics import MetricsCalculator
from src.portfolio import (
    AlertGenerator,
    AllocationAnalyzer,
    DeploymentAdvisor,
    HoldingsTracker,
    print_alerts,
    print_allocation_summary,
    print_deployment_plan,
)
from src.scoring import UniverseScorer


def test_portfolio():
    """Test portfolio management with sample data."""
    print("Testing Portfolio Management...")
    print("=" * 70)

    # Use temporary database for testing
    db_path = Path("data/test_portfolio.db")
    tracker = HoldingsTracker(db_path)

    # Clear any existing test data
    tracker.clear_all()

    # Add sample holdings
    print("\n1. Adding sample holdings...")

    sample_holdings = [
        # Tier 1 - Established (target 60%)
        ("MSFT", 10, 4500, "2024-01-15", "1", "Core tech holding"),
        ("JNJ", 15, 2200, "2024-02-01", "1", "Healthcare staple"),
        ("V", 8, 1800, "2024-03-01", "1", "Payments leader"),
        # Tier 2 - Growth (target 30%)
        ("HUBS", 5, 1500, "2024-04-01", "2", "SaaS growth"),
        ("CRWD", 4, 1200, "2024-05-01", "2", "Cybersecurity"),
        # Tier 3 - Opportunistic (target 10%)
        ("DDOG", 6, 800, "2024-06-01", "3", "Observability play"),
    ]

    for ticker, shares, cost, date_str, tier, notes in sample_holdings:
        tracker.add_holding(
            ticker=ticker,
            shares=shares,
            cost_basis=cost,
            purchase_date=date.fromisoformat(date_str),
            tier=tier,
            notes=notes,
        )
        print(f"   Added {shares} shares of {ticker} (Tier {tier})")

    # Get all positions
    print("\n2. Current positions...")
    positions = tracker.get_all_positions()
    for pos in positions:
        print(f"   {pos.ticker}: {pos.total_shares} shares, cost ${pos.total_cost:,.0f}")

    # Fetch current prices
    print("\n3. Fetching current prices...")
    client = YahooClient()
    prices = {}
    for pos in positions:
        quote = client.get_quote(pos.ticker)
        if quote:
            prices[pos.ticker] = quote.price
            print(f"   {pos.ticker}: ${quote.price:.2f}")

    # Analyze allocation
    print("\n4. Analyzing allocation...")
    analyzer = AllocationAnalyzer()
    allocation = analyzer.analyze(tracker, prices)
    print_allocation_summary(allocation)

    # Score the universe (small test set)
    print("\n5. Scoring investment candidates...")
    calculator = MetricsCalculator()
    scorer = UniverseScorer()

    test_universe = ["MSFT", "JNJ", "V", "HUBS", "CRWD", "DDOG", "AAPL", "COST", "SNOW", "GOOGL"]
    metrics_list = []

    for ticker in test_universe:
        print(f"   Scoring {ticker}...", end=" ")
        financials = client.get_company_financials(ticker, years=5)
        if financials:
            metrics = calculator.calculate(financials)
            metrics_list.append(metrics)
            print(f"✓ ({metrics.stage.stage.value})")
        else:
            print("✗")

    scores = scorer.score_universe(metrics_list)

    # Generate deployment recommendations
    print("\n6. Generating deployment recommendations...")
    advisor = DeploymentAdvisor()
    plan = advisor.recommend(
        capital=1000,  # £1000 to deploy
        tracker=tracker,
        prices=prices,
        scores=scores,
    )
    print_deployment_plan(plan)

    # Generate alerts
    print("\n7. Checking for alerts...")
    alert_gen = AlertGenerator()
    alerts = alert_gen.generate_all_alerts(
        allocation=allocation,
        current_scores=scores,
        previous_scores=None,  # No previous scores for first run
    )
    print_alerts(alerts)

    # Test transaction history
    print("\n8. Transaction history...")
    transactions = tracker.get_transactions()
    print(f"   Total transactions: {len(transactions)}")
    for tx in transactions[:3]:
        print(f"   {tx.transaction_date}: {tx.transaction_type} {tx.shares} {tx.ticker} @ ${tx.price_per_share:.2f}")

    # Cleanup test database
    db_path.unlink(missing_ok=True)
    print(f"\n✓ Cleaned up test database")

    print("\n" + "=" * 70)
    print("Portfolio management tests completed!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = test_portfolio()
    sys.exit(0 if success else 1)
