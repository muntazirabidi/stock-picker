"""Test metrics calculations with real company data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import YahooClient
from src.metrics import MetricsCalculator, print_metrics_summary


def test_metrics():
    """Test metrics calculation on various company types."""
    print("Testing Metrics Engine...")
    print("=" * 60)

    client = YahooClient()
    calculator = MetricsCalculator()

    # Test companies representing different stages
    test_cases = [
        ("COST", "Mature/Compounder - Costco"),
        ("MSFT", "Compounder - Microsoft"),
        ("HUBS", "Growth - HubSpot"),
        ("SNOW", "Growth - Snowflake"),
        ("JNJ", "Mature - Johnson & Johnson"),
    ]

    results = []

    for ticker, description in test_cases:
        print(f"\n{'='*60}")
        print(f"Fetching data for {ticker} ({description})...")

        financials = client.get_company_financials(ticker, years=5)

        if not financials:
            print(f"  ✗ Failed to fetch data for {ticker}")
            continue

        print(f"  ✓ Data fetched: {len(financials.income_statements)} years of financials")

        # Calculate metrics
        metrics = calculator.calculate(financials)
        results.append(metrics)

        # Print summary
        print_metrics_summary(metrics)

    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    stage_counts: dict[str, int] = {}
    for m in results:
        stage = m.stage.stage.value
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    print(f"\nCompanies analyzed: {len(results)}")
    print("By stage:")
    for stage, count in sorted(stage_counts.items()):
        print(f"  {stage}: {count}")

    # Show Rule of 40 for growth companies
    print("\nRule of 40 scores (growth companies):")
    for m in results:
        if m.growth_stage and m.growth_stage.efficiency.rule_of_40 is not None:
            r40 = m.growth_stage.efficiency.rule_of_40
            status = "✓" if r40 >= 40 else "⚠"
            print(f"  {m.ticker}: {r40:.1f} {status}")

    # Show ROIC for mature companies
    print("\nROIC (mature/compounders):")
    for m in results:
        if m.traditional and m.traditional.quality.roic is not None:
            roic = m.traditional.quality.roic
            status = "✓" if roic >= 0.15 else "⚠" if roic >= 0.10 else "✗"
            print(f"  {m.ticker}: {roic*100:.1f}% {status}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_metrics()
    sys.exit(0 if success else 1)
