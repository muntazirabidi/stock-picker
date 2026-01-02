"""Command-line interface for equity research system."""

import sys
from datetime import date
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Equity Research System - Find quality compounders."""
    pass


@main.command()
@click.option("--universe", "-u", default="sp500",
              type=click.Choice(["sp500", "nasdaq100", "all"]),
              help="Universe to refresh")
@click.option("--output", "-o", default="data/processed/universe.parquet",
              help="Output path for universe data")
def refresh(universe: str, output: str):
    """Refresh universe data and scores."""
    from src.data import YahooClient

    console.print(Panel.fit("🔄 Refreshing Universe Data", style="bold blue"))

    client = YahooClient()
    tickers = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if universe in ("sp500", "all"):
            task = progress.add_task("Fetching S&P 500...", total=None)
            sp500 = client.get_sp500_tickers()
            tickers.extend(sp500)
            progress.update(task, description=f"✓ S&P 500: {len(sp500)} stocks")

        if universe in ("nasdaq100", "all"):
            task = progress.add_task("Fetching Nasdaq 100...", total=None)
            nasdaq = client.get_nasdaq100_tickers()
            # Deduplicate
            new_tickers = [t for t in nasdaq if t not in tickers]
            tickers.extend(new_tickers)
            progress.update(task, description=f"✓ Nasdaq 100: {len(new_tickers)} new stocks")

    # Save universe
    import pandas as pd
    df = pd.DataFrame({"ticker": tickers})
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    console.print(f"\n✓ Saved {len(tickers)} tickers to {output}")
    console.print(f"  Cache stats: {client.cache_stats()}")


@main.command()
@click.argument("tickers", nargs=-1, required=True)
@click.option("--detailed", "-d", is_flag=True, help="Show detailed metrics")
def score(tickers: tuple, detailed: bool):
    """Score specific tickers."""
    from src.data import YahooClient
    from src.metrics import MetricsCalculator, print_metrics_summary
    from src.scoring import UniverseScorer, print_top_scores

    console.print(Panel.fit(f"📊 Scoring {len(tickers)} stocks", style="bold blue"))

    client = YahooClient()
    calculator = MetricsCalculator()
    scorer = UniverseScorer()

    metrics_list = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for ticker in tickers:
            task = progress.add_task(f"Fetching {ticker}...", total=None)
            financials = client.get_company_financials(ticker.upper(), years=5)

            if financials:
                metrics = calculator.calculate(financials)
                metrics_list.append(metrics)
                progress.update(task, description=f"✓ {ticker}: {metrics.stage.stage.value}")
            else:
                progress.update(task, description=f"✗ {ticker}: Failed to fetch")

    if not metrics_list:
        console.print("[red]No valid data fetched[/red]")
        return

    # Score
    scores = scorer.score_universe(metrics_list)

    # Display results
    table = Table(title="Stock Scores")
    table.add_column("Rank", style="cyan", justify="right")
    table.add_column("Ticker", style="bold")
    table.add_column("Name")
    table.add_column("Stage", style="magenta")
    table.add_column("Score", justify="right", style="green")

    for i, s in enumerate(scores, 1):
        score_str = f"{s.composite_score:.1f}" if s.composite_score else "N/A"
        name = (s.name or "")[:30]
        table.add_row(str(i), s.ticker, name, s.stage.value, score_str)

    console.print(table)

    if detailed:
        for metrics in metrics_list:
            print_metrics_summary(metrics)


@main.command()
@click.option("--amount", "-a", required=True, type=float, help="Amount to deploy")
@click.option("--db", default="data/portfolio.db", help="Portfolio database path")
def deploy(amount: float, db: str):
    """Get deployment recommendations for available capital."""
    from src.data import YahooClient
    from src.metrics import MetricsCalculator
    from src.portfolio import HoldingsTracker, DeploymentAdvisor, print_deployment_plan
    from src.scoring import UniverseScorer

    console.print(Panel.fit(f"💰 Deployment Plan for £{amount:,.0f}", style="bold green"))

    client = YahooClient()
    tracker = HoldingsTracker(db)
    calculator = MetricsCalculator()
    scorer = UniverseScorer()
    advisor = DeploymentAdvisor()

    # Get current positions
    positions = tracker.get_all_positions()

    if not positions:
        console.print("[yellow]No existing positions found. Add holdings first.[/yellow]")
        console.print("Use: equity-research portfolio add TICKER SHARES COST DATE TIER")
        return

    console.print(f"Found {len(positions)} existing positions")

    # Fetch prices and scores
    held_tickers = [p.ticker for p in positions]

    # Build candidate universe (held + some top stocks)
    candidate_tickers = list(set(held_tickers + ["AAPL", "MSFT", "GOOGL", "AMZN", "V", "MA"]))

    prices = {}
    metrics_list = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for ticker in candidate_tickers:
            task = progress.add_task(f"Fetching {ticker}...", total=None)
            financials = client.get_company_financials(ticker, years=5)

            if financials:
                if financials.quote:
                    prices[ticker] = financials.quote.price
                metrics = calculator.calculate(financials)
                metrics_list.append(metrics)
                progress.update(task, description=f"✓ {ticker}")
            else:
                progress.update(task, description=f"✗ {ticker}")

    scores = scorer.score_universe(metrics_list)

    # Generate recommendations
    plan = advisor.recommend(
        capital=amount,
        tracker=tracker,
        prices=prices,
        scores=scores,
    )

    print_deployment_plan(plan)


@main.group()
def portfolio():
    """Portfolio management commands."""
    pass


@portfolio.command("status")
@click.option("--db", default="data/portfolio.db", help="Portfolio database path")
@click.option("--alerts", "-a", is_flag=True, help="Show alerts")
def portfolio_status(db: str, alerts: bool):
    """Show portfolio status and allocation."""
    from src.data import YahooClient
    from src.metrics import MetricsCalculator
    from src.portfolio import (
        HoldingsTracker,
        AllocationAnalyzer,
        AlertGenerator,
        print_allocation_summary,
        print_alerts,
    )
    from src.scoring import UniverseScorer

    console.print(Panel.fit("📈 Portfolio Status", style="bold blue"))

    tracker = HoldingsTracker(db)
    positions = tracker.get_all_positions()

    if not positions:
        console.print("[yellow]No positions found.[/yellow]")
        return

    # Fetch current prices
    client = YahooClient()
    prices = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for pos in positions:
            task = progress.add_task(f"Fetching {pos.ticker}...", total=None)
            quote = client.get_quote(pos.ticker)
            if quote:
                prices[pos.ticker] = quote.price
            progress.update(task, description=f"✓ {pos.ticker}: ${prices.get(pos.ticker, 0):.2f}")

    # Analyze allocation
    analyzer = AllocationAnalyzer()
    allocation = analyzer.analyze(tracker, prices)
    print_allocation_summary(allocation)

    if alerts:
        # Generate alerts
        calculator = MetricsCalculator()
        scorer = UniverseScorer()

        metrics_list = []
        for pos in positions:
            financials = client.get_company_financials(pos.ticker, years=5)
            if financials:
                metrics_list.append(calculator.calculate(financials))

        scores = scorer.score_universe(metrics_list)

        alert_gen = AlertGenerator()
        alert_list = alert_gen.generate_all_alerts(allocation, scores)
        print_alerts(alert_list)


@portfolio.command("add")
@click.argument("ticker")
@click.argument("shares", type=float)
@click.argument("cost", type=float)
@click.argument("purchase_date")
@click.argument("tier", type=click.Choice(["1", "2", "3"]))
@click.option("--notes", "-n", default=None, help="Notes about the position")
@click.option("--db", default="data/portfolio.db", help="Portfolio database path")
def portfolio_add(ticker: str, shares: float, cost: float, purchase_date: str,
                  tier: str, notes: str, db: str):
    """Add a holding to the portfolio.

    Example: equity-research portfolio add MSFT 10 4500 2024-01-15 1
    """
    from src.portfolio import HoldingsTracker

    tracker = HoldingsTracker(db)

    try:
        pdate = date.fromisoformat(purchase_date)
    except ValueError:
        console.print(f"[red]Invalid date format. Use YYYY-MM-DD[/red]")
        return

    tracker.add_holding(
        ticker=ticker.upper(),
        shares=shares,
        cost_basis=cost,
        purchase_date=pdate,
        tier=tier,
        notes=notes,
    )

    console.print(f"✓ Added {shares} shares of {ticker.upper()} (Tier {tier})")
    console.print(f"  Cost basis: ${cost:,.2f}")
    console.print(f"  Purchase date: {pdate}")


@portfolio.command("list")
@click.option("--db", default="data/portfolio.db", help="Portfolio database path")
def portfolio_list(db: str):
    """List all holdings."""
    from src.portfolio import HoldingsTracker

    tracker = HoldingsTracker(db)
    positions = tracker.get_all_positions()

    if not positions:
        console.print("[yellow]No positions found.[/yellow]")
        return

    table = Table(title="Current Holdings")
    table.add_column("Ticker", style="bold")
    table.add_column("Shares", justify="right")
    table.add_column("Cost Basis", justify="right", style="cyan")
    table.add_column("Avg Cost", justify="right")
    table.add_column("Tier", justify="center")
    table.add_column("First Buy")

    total_cost = 0
    for pos in positions:
        tier_num = pos.tier.value.replace("tier_", "")
        table.add_row(
            pos.ticker,
            f"{pos.total_shares:.2f}",
            f"${pos.total_cost:,.2f}",
            f"${pos.cost_per_share:.2f}",
            tier_num,
            str(pos.first_purchase),
        )
        total_cost += pos.total_cost

    console.print(table)
    console.print(f"\nTotal Cost Basis: ${total_cost:,.2f}")
    console.print(f"Positions: {len(positions)}")


@portfolio.command("import")
@click.argument("csv_path", type=click.Path(exists=True))
@click.option("--db", default="data/portfolio.db", help="Portfolio database path")
def portfolio_import(csv_path: str, db: str):
    """Import holdings from CSV file.

    CSV format: ticker,shares,cost_basis,purchase_date,tier,notes
    """
    from src.portfolio import HoldingsTracker

    tracker = HoldingsTracker(db)
    count = tracker.import_from_csv(Path(csv_path))
    console.print(f"✓ Imported {count} holdings from {csv_path}")


@portfolio.command("export")
@click.argument("csv_path")
@click.option("--db", default="data/portfolio.db", help="Portfolio database path")
def portfolio_export(csv_path: str, db: str):
    """Export holdings to CSV file."""
    from src.portfolio import HoldingsTracker

    tracker = HoldingsTracker(db)
    count = tracker.export_to_csv(Path(csv_path))
    console.print(f"✓ Exported {count} holdings to {csv_path}")


@main.command()
def cache():
    """Show and manage cache."""
    from src.data import YahooClient

    client = YahooClient()
    stats = client.cache_stats()

    table = Table(title="Cache Statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Files", str(stats["total_files"]))
    table.add_row("Valid Entries", str(stats["valid"]))
    table.add_row("Expired Entries", str(stats["expired"]))
    table.add_row("Total Size", f"{stats['total_size_mb']:.2f} MB")
    table.add_row("TTL", f"{stats['ttl_hours']:.0f} hours")

    console.print(table)


@main.command("clear-cache")
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
def clear_cache():
    """Clear all cached data."""
    from src.data import YahooClient

    client = YahooClient()
    count = client.clear_cache()
    console.print(f"✓ Cleared {count} cache entries")


if __name__ == "__main__":
    main()
