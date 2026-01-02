"""Test scoring system with sample companies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import YahooClient
from src.metrics import MetricsCalculator
from src.scoring import (
    UniverseScorer,
    print_score_distribution,
    print_top_scores,
)


def test_scoring():
    """Test scoring system on a small universe."""
    print("Testing Scoring System...")
    print("=" * 60)

    client = YahooClient()
    calculator = MetricsCalculator()
    scorer = UniverseScorer()

    # Test universe - mix of company types
    test_tickers = [
        # Mature/Value
        "JNJ", "PG", "KO", "WMT",
        # Compounders
        "MSFT", "AAPL", "COST", "V",
        # Growth
        "HUBS", "SNOW", "CRWD", "DDOG",
    ]

    print(f"\nFetching data for {len(test_tickers)} companies...")

    # Fetch all company data
    all_metrics = []
    for ticker in test_tickers:
        print(f"  Fetching {ticker}...", end=" ")
        financials = client.get_company_financials(ticker, years=5)
        if financials:
            metrics = calculator.calculate(financials)
            all_metrics.append(metrics)
            print(f"✓ ({metrics.stage.stage.value})")
        else:
            print("✗ (failed)")

    print(f"\nSuccessfully fetched: {len(all_metrics)}/{len(test_tickers)}")

    # Score the universe
    print("\nScoring universe...")
    scores = scorer.score_universe(all_metrics)

    # Print results
    print_top_scores(scores, n=len(scores))

    # Print distribution
    print_score_distribution(scores)

    # Show detailed breakdown for top 3
    print(f"\n{'='*70}")
    print("DETAILED BREAKDOWN - TOP 3")
    print("=" * 70)

    for score in scores[:3]:
        print(f"\n{score.ticker} - {score.name}")
        print(f"  Stage: {score.stage.value}")
        print(f"  Composite Score: {score.composite_score:.1f}")
        print(f"  Percentile Rank: {score.percentile_rank}")

        if score.quality_score is not None:
            print(f"\n  Traditional Scores:")
            print(f"    Quality: {score.quality_score:.1f}")
            print(f"    Growth: {score.growth_score:.1f}" if score.growth_score else "    Growth: N/A")
            print(f"    Strength: {score.strength_score:.1f}" if score.strength_score else "    Strength: N/A")
            print(f"    Valuation: {score.valuation_score:.1f}" if score.valuation_score else "    Valuation: N/A")

        if score.efficiency_score is not None:
            print(f"\n  Growth Stage Scores:")
            print(f"    Revenue Quality: {score.revenue_quality_score:.1f}" if score.revenue_quality_score else "    Revenue Quality: N/A")
            print(f"    Efficiency: {score.efficiency_score:.1f}" if score.efficiency_score else "    Efficiency: N/A")

        print(f"\n  Key Metric Percentiles:")
        for metric, pct in sorted(score.metric_percentiles.items()):
            if pct is not None:
                print(f"    {metric}: {pct:.0f}th percentile")

    # Save to parquet
    output_path = Path("data/processed/test_scores.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scorer.save_scores(scores, output_path)
    print(f"\n✓ Scores saved to {output_path}")

    # Verify we can load it back
    df = scorer.load_scores(output_path)
    print(f"✓ Loaded back {len(df)} rows")

    print("\n" + "=" * 60)
    print("All scoring tests completed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_scoring()
    sys.exit(0 if success else 1)
