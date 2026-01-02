"""Portfolio allocation monitoring and analysis.

Tracks actual vs target allocation across tiers and identifies imbalances.
"""

from dataclasses import dataclass
from typing import Sequence

from src.data.models import Tier

from .holdings import HoldingsTracker, Position


@dataclass
class TierAllocation:
    """Allocation data for a single tier."""

    tier: Tier
    target_pct: float  # Target allocation percentage (0-1)
    actual_pct: float  # Actual allocation percentage (0-1)
    actual_value: float  # Current market value
    target_value: float  # Target value based on total portfolio
    num_positions: int
    positions: list[Position]

    @property
    def difference_pct(self) -> float:
        """Difference between actual and target (positive = overweight)."""
        return self.actual_pct - self.target_pct

    @property
    def difference_value(self) -> float:
        """Dollar difference between actual and target."""
        return self.actual_value - self.target_value

    @property
    def is_underweight(self) -> bool:
        """True if significantly underweight (>2% below target)."""
        return self.difference_pct < -0.02

    @property
    def is_overweight(self) -> bool:
        """True if significantly overweight (>2% above target)."""
        return self.difference_pct > 0.02


@dataclass
class PositionAllocation:
    """Allocation data for a single position."""

    ticker: str
    tier: Tier
    shares: float
    cost_basis: float
    current_price: float
    current_value: float
    weight_pct: float  # Weight in total portfolio
    weight_in_tier_pct: float  # Weight within tier
    gain_loss_pct: float
    max_position_pct: float  # Max allowed position size

    @property
    def is_oversized(self) -> bool:
        """True if position exceeds max allowed size."""
        return self.weight_pct > self.max_position_pct


@dataclass
class AllocationSummary:
    """Complete portfolio allocation analysis."""

    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_pct: float
    tier_allocations: dict[Tier, TierAllocation]
    position_allocations: list[PositionAllocation]
    num_positions: int

    @property
    def most_underweight_tier(self) -> Tier | None:
        """Get the most underweight tier."""
        underweight = [
            (tier, alloc.difference_pct)
            for tier, alloc in self.tier_allocations.items()
            if alloc.is_underweight
        ]
        if not underweight:
            return None
        return min(underweight, key=lambda x: x[1])[0]


# Default allocation targets
DEFAULT_TIER_TARGETS = {
    Tier.TIER_1: 0.60,  # 60% in established compounders
    Tier.TIER_2: 0.30,  # 30% in high growth
    Tier.TIER_3: 0.10,  # 10% in opportunistic
}

# Default position limits
DEFAULT_POSITION_LIMITS = {
    Tier.TIER_1: 0.08,  # 8% max per position
    Tier.TIER_2: 0.05,  # 5% max per position
    Tier.TIER_3: 0.03,  # 3% max per position
}


class AllocationAnalyzer:
    """Analyzes portfolio allocation vs targets."""

    def __init__(
        self,
        tier_targets: dict[Tier, float] | None = None,
        position_limits: dict[Tier, float] | None = None,
    ):
        """Initialize analyzer.

        Args:
            tier_targets: Target allocation per tier (should sum to 1.0)
            position_limits: Max position size per tier
        """
        self.tier_targets = tier_targets or DEFAULT_TIER_TARGETS
        self.position_limits = position_limits or DEFAULT_POSITION_LIMITS

    def analyze(
        self,
        tracker: HoldingsTracker,
        prices: dict[str, float],
    ) -> AllocationSummary:
        """Analyze current portfolio allocation.

        Args:
            tracker: HoldingsTracker with current positions
            prices: Dict mapping ticker to current price

        Returns:
            AllocationSummary with complete analysis
        """
        positions = tracker.get_all_positions()

        if not positions:
            return AllocationSummary(
                total_value=0,
                total_cost=0,
                total_gain_loss=0,
                total_gain_loss_pct=0,
                tier_allocations={
                    tier: TierAllocation(
                        tier=tier,
                        target_pct=target,
                        actual_pct=0,
                        actual_value=0,
                        target_value=0,
                        num_positions=0,
                        positions=[],
                    )
                    for tier, target in self.tier_targets.items()
                },
                position_allocations=[],
                num_positions=0,
            )

        # Calculate totals
        total_value = 0
        total_cost = 0
        position_values: dict[str, float] = {}

        for pos in positions:
            price = prices.get(pos.ticker, 0)
            value = pos.current_value(price)
            position_values[pos.ticker] = value
            total_value += value
            total_cost += pos.total_cost

        total_gain_loss = total_value - total_cost
        total_gain_loss_pct = total_gain_loss / total_cost if total_cost > 0 else 0

        # Group by tier
        positions_by_tier = tracker.get_positions_by_tier()

        # Calculate tier allocations
        tier_allocations: dict[Tier, TierAllocation] = {}

        for tier, target_pct in self.tier_targets.items():
            tier_positions = positions_by_tier.get(tier, [])
            tier_value = sum(position_values.get(p.ticker, 0) for p in tier_positions)
            actual_pct = tier_value / total_value if total_value > 0 else 0

            tier_allocations[tier] = TierAllocation(
                tier=tier,
                target_pct=target_pct,
                actual_pct=actual_pct,
                actual_value=tier_value,
                target_value=total_value * target_pct,
                num_positions=len(tier_positions),
                positions=tier_positions,
            )

        # Calculate position allocations
        position_allocations: list[PositionAllocation] = []

        for pos in positions:
            price = prices.get(pos.ticker, 0)
            value = position_values.get(pos.ticker, 0)
            weight_pct = value / total_value if total_value > 0 else 0

            # Weight within tier
            tier_alloc = tier_allocations[pos.tier]
            weight_in_tier = value / tier_alloc.actual_value if tier_alloc.actual_value > 0 else 0

            position_allocations.append(
                PositionAllocation(
                    ticker=pos.ticker,
                    tier=pos.tier,
                    shares=pos.total_shares,
                    cost_basis=pos.total_cost,
                    current_price=price,
                    current_value=value,
                    weight_pct=weight_pct,
                    weight_in_tier_pct=weight_in_tier,
                    gain_loss_pct=pos.gain_loss_pct(price),
                    max_position_pct=self.position_limits.get(pos.tier, 0.05),
                )
            )

        # Sort by weight
        position_allocations.sort(key=lambda p: p.weight_pct, reverse=True)

        return AllocationSummary(
            total_value=total_value,
            total_cost=total_cost,
            total_gain_loss=total_gain_loss,
            total_gain_loss_pct=total_gain_loss_pct,
            tier_allocations=tier_allocations,
            position_allocations=position_allocations,
            num_positions=len(positions),
        )


def print_allocation_summary(summary: AllocationSummary) -> None:
    """Print formatted allocation summary.

    Args:
        summary: AllocationSummary to print
    """
    print(f"\n{'='*70}")
    print("PORTFOLIO ALLOCATION SUMMARY")
    print(f"{'='*70}")

    # Overall stats
    print(f"\nTotal Value: ${summary.total_value:,.2f}")
    print(f"Total Cost: ${summary.total_cost:,.2f}")
    gain_sign = "+" if summary.total_gain_loss >= 0 else ""
    print(f"Total Gain/Loss: {gain_sign}${summary.total_gain_loss:,.2f} ({gain_sign}{summary.total_gain_loss_pct*100:.1f}%)")
    print(f"Positions: {summary.num_positions}")

    # Tier allocation
    print(f"\n{'='*70}")
    print("TIER ALLOCATION")
    print(f"{'='*70}")
    print(f"{'Tier':<12} {'Target':>10} {'Actual':>10} {'Diff':>10} {'Value':>15} {'Status':>10}")
    print("-" * 70)

    for tier in [Tier.TIER_1, Tier.TIER_2, Tier.TIER_3]:
        alloc = summary.tier_allocations[tier]
        diff_sign = "+" if alloc.difference_pct >= 0 else ""

        if alloc.is_underweight:
            status = "⚠️ Under"
        elif alloc.is_overweight:
            status = "⚠️ Over"
        else:
            status = "✓ OK"

        tier_name = tier.value.replace("tier_", "Tier ")
        print(
            f"{tier_name:<12} "
            f"{alloc.target_pct*100:>9.1f}% "
            f"{alloc.actual_pct*100:>9.1f}% "
            f"{diff_sign}{alloc.difference_pct*100:>8.1f}% "
            f"${alloc.actual_value:>13,.0f} "
            f"{status:>10}"
        )

    # Position details
    print(f"\n{'='*70}")
    print("POSITION DETAILS")
    print(f"{'='*70}")
    print(f"{'Ticker':<8} {'Tier':>6} {'Weight':>8} {'Value':>12} {'Gain/Loss':>12} {'Status':>10}")
    print("-" * 70)

    for pos in summary.position_allocations:
        gain_sign = "+" if pos.gain_loss_pct >= 0 else ""
        status = "⚠️ Large" if pos.is_oversized else ""

        tier_num = pos.tier.value.replace("tier_", "")
        print(
            f"{pos.ticker:<8} "
            f"{tier_num:>6} "
            f"{pos.weight_pct*100:>7.1f}% "
            f"${pos.current_value:>10,.0f} "
            f"{gain_sign}{pos.gain_loss_pct*100:>10.1f}% "
            f"{status:>10}"
        )

    print("=" * 70)
