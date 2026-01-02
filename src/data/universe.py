"""Universe management - loading stocks from multiple sources."""

import csv
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from .fmp_client import FMPClient
from .models import Tier, UniverseStock


class UniverseLoader:
    """Load and manage the stock universe from multiple sources.

    Sources:
    - S&P 500 (Tier 1)
    - S&P 400 MidCap (Tier 1) - via screening
    - Nasdaq 100 (Tier 2)
    - Manual watchlist (Tier 3)
    """

    def __init__(self, fmp_client: FMPClient, watchlist_path: Path | None = None):
        self.fmp = fmp_client
        self.watchlist_path = watchlist_path or Path("watchlist.csv")

    def load_sp500(self) -> list[UniverseStock]:
        """Load S&P 500 constituents (Tier 1).

        Returns:
            List of UniverseStock entries
        """
        data = self.fmp.get_sp500_constituents()
        return self._convert_constituents(data, Tier.TIER_1, "sp500")

    def load_nasdaq100(self) -> list[UniverseStock]:
        """Load Nasdaq 100 constituents (Tier 2).

        Returns:
            List of UniverseStock entries
        """
        data = self.fmp.get_nasdaq100_constituents()
        return self._convert_constituents(data, Tier.TIER_2, "nasdaq100")

    def load_midcap_screen(
        self,
        min_market_cap: int = 2_000_000_000,
        max_market_cap: int = 20_000_000_000,
    ) -> list[UniverseStock]:
        """Load mid-cap stocks via screener (approximates S&P 400).

        Args:
            min_market_cap: Minimum market cap (default $2B)
            max_market_cap: Maximum market cap (default $20B)

        Returns:
            List of UniverseStock entries
        """
        data = self.fmp.stock_screener(
            market_cap_min=min_market_cap,
            market_cap_max=max_market_cap,
            exchange="NYSE,NASDAQ",
            limit=500,
        )

        stocks = []
        for item in data:
            if not item.get("symbol"):
                continue

            stocks.append(
                UniverseStock(
                    ticker=item["symbol"],
                    name=item.get("companyName"),
                    tier=Tier.TIER_1,
                    source="midcap_screen",
                    market_cap=item.get("marketCap"),
                    sector=item.get("sector"),
                )
            )

        return stocks

    def load_growth_screen(
        self,
        min_market_cap: int = 2_000_000_000,
        max_market_cap: int = 50_000_000_000,
    ) -> list[UniverseStock]:
        """Load growth stocks via screener (Tier 2).

        Args:
            min_market_cap: Minimum market cap (default $2B)
            max_market_cap: Maximum market cap (default $50B)

        Returns:
            List of UniverseStock entries
        """
        # Screen for Technology and Healthcare sectors (growth-heavy)
        stocks = []

        for sector in ["Technology", "Healthcare", "Consumer Cyclical"]:
            data = self.fmp.stock_screener(
                market_cap_min=min_market_cap,
                market_cap_max=max_market_cap,
                sector=sector,
                exchange="NYSE,NASDAQ",
                limit=200,
            )

            for item in data:
                if not item.get("symbol"):
                    continue

                stocks.append(
                    UniverseStock(
                        ticker=item["symbol"],
                        name=item.get("companyName"),
                        tier=Tier.TIER_2,
                        source="growth_screen",
                        market_cap=item.get("marketCap"),
                        sector=item.get("sector"),
                    )
                )

        return stocks

    def load_watchlist(self) -> list[UniverseStock]:
        """Load manual watchlist from CSV file (Tier 3).

        Expected CSV format:
        ticker,tier,notes,added_date

        Returns:
            List of UniverseStock entries
        """
        if not self.watchlist_path.exists():
            return []

        stocks = []

        with open(self.watchlist_path, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip comment lines
                ticker = row.get("ticker", "").strip()
                if not ticker or ticker.startswith("#"):
                    continue

                # Parse tier (default to 3)
                tier_str = row.get("tier", "3")
                try:
                    tier = Tier(f"tier_{tier_str}")
                except ValueError:
                    tier = Tier.TIER_3

                # Parse date
                added_date = None
                if row.get("added_date"):
                    try:
                        added_date = date.fromisoformat(row["added_date"])
                    except ValueError:
                        pass

                stocks.append(
                    UniverseStock(
                        ticker=ticker,
                        name=None,  # Will be enriched later
                        tier=tier,
                        source="watchlist",
                        notes=row.get("notes"),
                        added_date=added_date,
                    )
                )

        return stocks

    def load_full_universe(
        self,
        include_sp500: bool = True,
        include_nasdaq100: bool = True,
        include_midcap: bool = True,
        include_growth_screen: bool = False,
        include_watchlist: bool = True,
    ) -> list[UniverseStock]:
        """Load complete universe from all configured sources.

        Args:
            include_sp500: Include S&P 500
            include_nasdaq100: Include Nasdaq 100
            include_midcap: Include mid-cap screener
            include_growth_screen: Include growth screener
            include_watchlist: Include manual watchlist

        Returns:
            Deduplicated list of UniverseStock
        """
        all_stocks: list[UniverseStock] = []

        if include_sp500:
            all_stocks.extend(self.load_sp500())

        if include_nasdaq100:
            all_stocks.extend(self.load_nasdaq100())

        if include_midcap:
            all_stocks.extend(self.load_midcap_screen())

        if include_growth_screen:
            all_stocks.extend(self.load_growth_screen())

        if include_watchlist:
            all_stocks.extend(self.load_watchlist())

        # Deduplicate by ticker, keeping first occurrence (priority order)
        seen = set()
        unique_stocks = []

        for stock in all_stocks:
            if stock.ticker not in seen:
                seen.add(stock.ticker)
                unique_stocks.append(stock)

        return unique_stocks

    def _convert_constituents(
        self, data: list[dict[str, Any]], tier: Tier, source: str
    ) -> list[UniverseStock]:
        """Convert FMP constituent data to UniverseStock models.

        Args:
            data: Raw API response
            tier: Universe tier
            source: Source identifier

        Returns:
            List of UniverseStock
        """
        stocks = []

        for item in data:
            if not item.get("symbol"):
                continue

            stocks.append(
                UniverseStock(
                    ticker=item["symbol"],
                    name=item.get("name") or item.get("companyName"),
                    tier=tier,
                    source=source,
                    sector=item.get("sector"),
                )
            )

        return stocks

    def to_dataframe(self, stocks: list[UniverseStock]) -> pd.DataFrame:
        """Convert universe to pandas DataFrame.

        Args:
            stocks: List of UniverseStock

        Returns:
            DataFrame with universe data
        """
        data = [
            {
                "ticker": s.ticker,
                "name": s.name,
                "tier": s.tier.value,
                "source": s.source,
                "market_cap": s.market_cap,
                "sector": s.sector,
                "added_date": s.added_date,
                "notes": s.notes,
            }
            for s in stocks
        ]

        return pd.DataFrame(data)

    def save_universe(self, stocks: list[UniverseStock], path: Path) -> None:
        """Save universe to parquet file.

        Args:
            stocks: List of UniverseStock
            path: Output path (.parquet)
        """
        df = self.to_dataframe(stocks)
        df.to_parquet(path, index=False)

    def load_universe_from_file(self, path: Path) -> list[UniverseStock]:
        """Load universe from parquet file.

        Args:
            path: Path to parquet file

        Returns:
            List of UniverseStock
        """
        df = pd.read_parquet(path)
        stocks = []

        for _, row in df.iterrows():
            try:
                tier = Tier(row["tier"])
            except ValueError:
                tier = Tier.TIER_3

            added_date = None
            if pd.notna(row.get("added_date")):
                added_date = row["added_date"]
                if isinstance(added_date, str):
                    added_date = date.fromisoformat(added_date)

            stocks.append(
                UniverseStock(
                    ticker=row["ticker"],
                    name=row.get("name"),
                    tier=tier,
                    source=row.get("source", "file"),
                    market_cap=row.get("market_cap"),
                    sector=row.get("sector"),
                    added_date=added_date,
                    notes=row.get("notes"),
                )
            )

        return stocks


def get_universe_summary(stocks: list[UniverseStock]) -> dict[str, Any]:
    """Get summary statistics for universe.

    Args:
        stocks: List of UniverseStock

    Returns:
        Summary dict with counts by tier, source, sector
    """
    tier_counts = {}
    source_counts = {}
    sector_counts = {}

    for stock in stocks:
        tier_counts[stock.tier.value] = tier_counts.get(stock.tier.value, 0) + 1
        source_counts[stock.source] = source_counts.get(stock.source, 0) + 1
        if stock.sector:
            sector_counts[stock.sector] = sector_counts.get(stock.sector, 0) + 1

    return {
        "total": len(stocks),
        "by_tier": tier_counts,
        "by_source": source_counts,
        "by_sector": sector_counts,
    }
