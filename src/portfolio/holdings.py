"""Holdings tracking with SQLite persistence.

Tracks portfolio positions, cost basis, and transaction history.
"""

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Sequence

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.data.models import Tier

Base = declarative_base()


class HoldingRecord(Base):
    """SQLAlchemy model for holdings."""

    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    shares = Column(Float, nullable=False)
    cost_basis = Column(Float, nullable=False)  # Total cost
    purchase_date = Column(Date, nullable=False)
    tier = Column(String(10), nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TransactionRecord(Base):
    """SQLAlchemy model for transactions."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL
    shares = Column(Float, nullable=False)
    price_per_share = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    transaction_date = Column(Date, nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


@dataclass
class Position:
    """Aggregated position for a ticker."""

    ticker: str
    total_shares: float
    total_cost: float
    tier: Tier
    first_purchase: date
    last_purchase: date
    notes: str | None = None

    @property
    def cost_per_share(self) -> float:
        """Average cost per share."""
        return self.total_cost / self.total_shares if self.total_shares > 0 else 0

    def current_value(self, price: float) -> float:
        """Calculate current market value."""
        return self.total_shares * price

    def gain_loss(self, price: float) -> float:
        """Calculate unrealized gain/loss."""
        return self.current_value(price) - self.total_cost

    def gain_loss_pct(self, price: float) -> float:
        """Calculate gain/loss percentage."""
        if self.total_cost <= 0:
            return 0
        return (self.current_value(price) - self.total_cost) / self.total_cost


class HoldingsTracker:
    """Tracks portfolio holdings with SQLite persistence."""

    def __init__(self, db_path: Path | str = "data/portfolio.db"):
        """Initialize holdings tracker.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_holding(
        self,
        ticker: str,
        shares: float,
        cost_basis: float,
        purchase_date: date,
        tier: Tier | str,
        notes: str | None = None,
    ) -> HoldingRecord:
        """Add a new holding.

        Args:
            ticker: Stock ticker
            shares: Number of shares
            cost_basis: Total cost (not per share)
            purchase_date: Date of purchase
            tier: Universe tier (1, 2, or 3)
            notes: Optional notes

        Returns:
            Created HoldingRecord
        """
        if isinstance(tier, str):
            tier = Tier(tier) if tier.startswith("tier_") else Tier(f"tier_{tier}")

        with Session(self.engine) as session:
            holding = HoldingRecord(
                ticker=ticker.upper(),
                shares=shares,
                cost_basis=cost_basis,
                purchase_date=purchase_date,
                tier=tier.value,
                notes=notes,
            )
            session.add(holding)

            # Also record as transaction
            transaction = TransactionRecord(
                ticker=ticker.upper(),
                transaction_type="BUY",
                shares=shares,
                price_per_share=cost_basis / shares if shares > 0 else 0,
                total_amount=cost_basis,
                transaction_date=purchase_date,
                notes=notes,
            )
            session.add(transaction)

            session.commit()
            session.refresh(holding)
            return holding

    def sell_holding(
        self,
        ticker: str,
        shares: float,
        price_per_share: float,
        sell_date: date,
        notes: str | None = None,
    ) -> bool:
        """Record a sale (reduces position).

        Args:
            ticker: Stock ticker
            shares: Number of shares to sell
            price_per_share: Sale price per share
            sell_date: Date of sale
            notes: Optional notes

        Returns:
            True if successful, False if insufficient shares
        """
        ticker = ticker.upper()

        with Session(self.engine) as session:
            # Get current position
            total_shares = (
                session.query(func.sum(HoldingRecord.shares))
                .filter(HoldingRecord.ticker == ticker)
                .scalar()
            ) or 0

            if total_shares < shares:
                return False

            # Record transaction
            transaction = TransactionRecord(
                ticker=ticker,
                transaction_type="SELL",
                shares=shares,
                price_per_share=price_per_share,
                total_amount=shares * price_per_share,
                transaction_date=sell_date,
                notes=notes,
            )
            session.add(transaction)

            # Reduce holdings (FIFO - reduce oldest first)
            holdings = (
                session.query(HoldingRecord)
                .filter(HoldingRecord.ticker == ticker)
                .order_by(HoldingRecord.purchase_date)
                .all()
            )

            remaining_to_sell = shares
            for holding in holdings:
                if remaining_to_sell <= 0:
                    break

                if holding.shares <= remaining_to_sell:
                    remaining_to_sell -= holding.shares
                    session.delete(holding)
                else:
                    # Partial sale
                    fraction_sold = remaining_to_sell / holding.shares
                    holding.shares -= remaining_to_sell
                    holding.cost_basis *= (1 - fraction_sold)
                    remaining_to_sell = 0

            session.commit()
            return True

    def get_position(self, ticker: str) -> Position | None:
        """Get aggregated position for a ticker.

        Args:
            ticker: Stock ticker

        Returns:
            Position or None if not held
        """
        ticker = ticker.upper()

        with Session(self.engine) as session:
            holdings = (
                session.query(HoldingRecord)
                .filter(HoldingRecord.ticker == ticker)
                .all()
            )

            if not holdings:
                return None

            total_shares = sum(h.shares for h in holdings)
            total_cost = sum(h.cost_basis for h in holdings)
            dates = [h.purchase_date for h in holdings]
            tier = Tier(holdings[0].tier)
            notes = holdings[0].notes

            return Position(
                ticker=ticker,
                total_shares=total_shares,
                total_cost=total_cost,
                tier=tier,
                first_purchase=min(dates),
                last_purchase=max(dates),
                notes=notes,
            )

    def get_all_positions(self) -> list[Position]:
        """Get all current positions.

        Returns:
            List of Position objects
        """
        with Session(self.engine) as session:
            tickers = (
                session.query(HoldingRecord.ticker)
                .distinct()
                .all()
            )

        positions = []
        for (ticker,) in tickers:
            position = self.get_position(ticker)
            if position:
                positions.append(position)

        return sorted(positions, key=lambda p: p.total_cost, reverse=True)

    def get_positions_by_tier(self) -> dict[Tier, list[Position]]:
        """Get positions grouped by tier.

        Returns:
            Dict mapping Tier to list of Positions
        """
        positions = self.get_all_positions()
        by_tier: dict[Tier, list[Position]] = {
            Tier.TIER_1: [],
            Tier.TIER_2: [],
            Tier.TIER_3: [],
        }

        for position in positions:
            by_tier[position.tier].append(position)

        return by_tier

    def get_total_value(self, prices: dict[str, float]) -> float:
        """Get total portfolio value at current prices.

        Args:
            prices: Dict mapping ticker to current price

        Returns:
            Total market value
        """
        total = 0
        for position in self.get_all_positions():
            if position.ticker in prices:
                total += position.current_value(prices[position.ticker])
        return total

    def get_total_cost(self) -> float:
        """Get total cost basis of portfolio.

        Returns:
            Total cost basis
        """
        return sum(p.total_cost for p in self.get_all_positions())

    def get_transactions(
        self,
        ticker: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TransactionRecord]:
        """Get transaction history.

        Args:
            ticker: Optional ticker filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of TransactionRecord
        """
        with Session(self.engine) as session:
            query = session.query(TransactionRecord)

            if ticker:
                query = query.filter(TransactionRecord.ticker == ticker.upper())
            if start_date:
                query = query.filter(TransactionRecord.transaction_date >= start_date)
            if end_date:
                query = query.filter(TransactionRecord.transaction_date <= end_date)

            return query.order_by(TransactionRecord.transaction_date.desc()).all()

    def import_from_csv(self, csv_path: Path) -> int:
        """Import holdings from CSV file.

        Expected format: ticker,shares,cost_basis,purchase_date,tier,notes

        Args:
            csv_path: Path to CSV file

        Returns:
            Number of holdings imported
        """
        count = 0

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                ticker = row.get("ticker", "").strip()
                if not ticker or ticker.startswith("#"):
                    continue

                try:
                    shares = float(row.get("shares", 0))
                    cost_basis = float(row.get("cost_basis", 0))
                    purchase_date = date.fromisoformat(row.get("purchase_date", ""))
                    tier = row.get("tier", "1")
                    notes = row.get("notes")

                    self.add_holding(
                        ticker=ticker,
                        shares=shares,
                        cost_basis=cost_basis,
                        purchase_date=purchase_date,
                        tier=tier,
                        notes=notes,
                    )
                    count += 1

                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid row for {ticker}: {e}")
                    continue

        return count

    def export_to_csv(self, csv_path: Path) -> int:
        """Export holdings to CSV file.

        Args:
            csv_path: Path to CSV file

        Returns:
            Number of holdings exported
        """
        positions = self.get_all_positions()

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ticker", "shares", "cost_basis", "purchase_date", "tier", "notes"])

            for pos in positions:
                writer.writerow([
                    pos.ticker,
                    pos.total_shares,
                    pos.total_cost,
                    pos.last_purchase.isoformat(),
                    pos.tier.value.replace("tier_", ""),
                    pos.notes or "",
                ])

        return len(positions)

    def clear_all(self) -> None:
        """Clear all holdings and transactions (use with caution!)."""
        with Session(self.engine) as session:
            session.query(HoldingRecord).delete()
            session.query(TransactionRecord).delete()
            session.commit()
