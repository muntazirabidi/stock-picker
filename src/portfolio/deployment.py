"""Monthly deployment recommendations.

Given available capital, recommends which stocks to buy based on:
1. Tier allocation (prioritize underweight tiers)
2. Stock scores (prefer higher-scoring stocks)
3. Position sizing (don't exceed max position size)
"""

from dataclasses import dataclass
from typing import Sequence

from src.data.models import Tier
from src.scoring import CompanyScore

from .allocation import AllocationAnalyzer, AllocationSummary
from .holdings import HoldingsTracker


@dataclass
class BuyRecommendation:
    """Single buy recommendation."""

    ticker: str
    amount: float  # Dollar amount to invest
    shares_estimate: float  # Estimated shares at current price
    tier: Tier
    score: float | None
    reason: str
    current_price: float
    current_weight_pct: float  # Current portfolio weight
    new_weight_pct: float  # Weight after purchase


@dataclass
class DeploymentPlan:
    """Complete deployment plan for available capital."""

    available_capital: float
    total_deployed: float
    remaining_cash: float
    recommendations: list[BuyRecommendation]
    reasoning: list[str]

    @property
    def num_buys(self) -> int:
        """Number of buy recommendations."""
        return len(self.recommendations)


# Minimum purchase size (avoid tiny orders)
MIN_PURCHASE_SIZE = 200.0

# Maximum recommendations per deployment
MAX_RECOMMENDATIONS = 5


class DeploymentAdvisor:
    """Generates monthly deployment recommendations."""

    def __init__(
        self,
        min_purchase: float = MIN_PURCHASE_SIZE,
        max_recommendations: int = MAX_RECOMMENDATIONS,
    ):
        """Initialize advisor.

        Args:
            min_purchase: Minimum purchase size in dollars
            max_recommendations: Max number of buy recommendations
        """
        self.min_purchase = min_purchase
        self.max_recommendations = max_recommendations
        self.allocation_analyzer = AllocationAnalyzer()

    def recommend(
        self,
        capital: float,
        tracker: HoldingsTracker,
        prices: dict[str, float],
        scores: Sequence[CompanyScore],
    ) -> DeploymentPlan:
        """Generate deployment recommendations.

        Args:
            capital: Available capital to deploy
            tracker: Current holdings
            prices: Current stock prices
            scores: Scored universe of stocks

        Returns:
            DeploymentPlan with recommendations
        """
        reasoning: list[str] = []
        recommendations: list[BuyRecommendation] = []

        if capital < self.min_purchase:
            reasoning.append(f"Capital ${capital:.0f} below minimum ${self.min_purchase:.0f}")
            return DeploymentPlan(
                available_capital=capital,
                total_deployed=0,
                remaining_cash=capital,
                recommendations=[],
                reasoning=reasoning,
            )

        # Get current allocation
        allocation = self.allocation_analyzer.analyze(tracker, prices)

        # Create score lookup
        score_lookup = {s.ticker: s for s in scores}

        remaining = capital
        portfolio_value = allocation.total_value + capital  # Projected value after deployment

        # Step 1: Identify underweight tiers
        underweight_tiers = [
            (tier, alloc)
            for tier, alloc in allocation.tier_allocations.items()
            if alloc.difference_pct < -0.01  # At least 1% underweight
        ]
        underweight_tiers.sort(key=lambda x: x[1].difference_pct)  # Most underweight first

        if underweight_tiers:
            most_underweight = underweight_tiers[0][0]
            reasoning.append(
                f"Tier {most_underweight.value.replace('tier_', '')} is most underweight "
                f"({underweight_tiers[0][1].difference_pct*100:.1f}% below target)"
            )
        else:
            reasoning.append("All tiers approximately at target allocation")

        # Step 2: Get candidate stocks for each tier
        tier_candidates: dict[Tier, list[CompanyScore]] = {
            Tier.TIER_1: [],
            Tier.TIER_2: [],
            Tier.TIER_3: [],
        }

        for score in scores:
            if score.composite_score is None:
                continue
            tier_candidates[score.stage_to_tier()].append(score)

        # Sort by score within each tier
        for tier in tier_candidates:
            tier_candidates[tier].sort(
                key=lambda s: s.composite_score or 0, reverse=True
            )

        # Step 3: Allocate capital
        # Prioritize underweight tiers, but also add to existing positions
        tiers_to_consider = []

        # First pass: underweight tiers
        for tier, alloc in underweight_tiers:
            shortfall = alloc.target_value - alloc.actual_value
            if shortfall > self.min_purchase:
                tiers_to_consider.append((tier, min(shortfall, remaining * 0.5)))

        # Second pass: proportional allocation if no underweight
        if not tiers_to_consider:
            for tier, target in self.allocation_analyzer.tier_targets.items():
                tiers_to_consider.append((tier, remaining * target))

        # Generate recommendations
        for tier, suggested_amount in tiers_to_consider:
            if remaining < self.min_purchase:
                break

            if len(recommendations) >= self.max_recommendations:
                break

            candidates = tier_candidates[tier][:10]  # Top 10 in tier

            for candidate in candidates:
                if remaining < self.min_purchase:
                    break

                if len(recommendations) >= self.max_recommendations:
                    break

                ticker = candidate.ticker
                price = prices.get(ticker, 0)

                if price <= 0:
                    continue

                # Check current position size
                current_position = next(
                    (p for p in allocation.position_allocations if p.ticker == ticker),
                    None,
                )
                current_weight = current_position.weight_pct if current_position else 0
                max_weight = self.allocation_analyzer.position_limits.get(tier, 0.05)

                # Calculate max additional investment
                current_value = current_position.current_value if current_position else 0
                max_position_value = portfolio_value * max_weight
                max_additional = max_position_value - current_value

                if max_additional < self.min_purchase:
                    continue

                # Determine amount to invest
                amount = min(
                    suggested_amount,
                    max_additional,
                    remaining,
                    capital * 0.4,  # Max 40% of deployment in single stock
                )

                if amount < self.min_purchase:
                    continue

                # Calculate new weight
                new_value = current_value + amount
                new_weight = new_value / portfolio_value

                # Build reason
                reason_parts = []
                if current_position:
                    reason_parts.append(f"Adding to position")
                else:
                    reason_parts.append("New position")

                if candidate.composite_score:
                    reason_parts.append(f"Score: {candidate.composite_score:.0f}")

                tier_alloc = allocation.tier_allocations[tier]
                if tier_alloc.is_underweight:
                    reason_parts.append(f"Tier {tier.value.replace('tier_', '')} underweight")

                recommendations.append(
                    BuyRecommendation(
                        ticker=ticker,
                        amount=amount,
                        shares_estimate=amount / price,
                        tier=tier,
                        score=candidate.composite_score,
                        reason="; ".join(reason_parts),
                        current_price=price,
                        current_weight_pct=current_weight,
                        new_weight_pct=new_weight,
                    )
                )

                remaining -= amount
                suggested_amount -= amount

        total_deployed = capital - remaining

        if not recommendations:
            reasoning.append("No suitable investment opportunities found")
        else:
            reasoning.append(f"Recommended {len(recommendations)} buys totaling ${total_deployed:.0f}")

        return DeploymentPlan(
            available_capital=capital,
            total_deployed=total_deployed,
            remaining_cash=remaining,
            recommendations=recommendations,
            reasoning=reasoning,
        )


# Add helper method to CompanyScore for tier mapping
def _stage_to_tier(self) -> Tier:
    """Map company stage to universe tier."""
    from src.data.models import CompanyStage

    # self.stage is already a CompanyStage enum on CompanyScore
    stage_tier_map = {
        CompanyStage.MATURE: Tier.TIER_1,
        CompanyStage.COMPOUNDER: Tier.TIER_2,  # Compounders go to growth tier
        CompanyStage.GROWTH: Tier.TIER_2,
        CompanyStage.SPECULATIVE: Tier.TIER_3,
    }
    return stage_tier_map.get(self.stage, Tier.TIER_3)


# Monkey-patch the method onto CompanyScore
CompanyScore.stage_to_tier = _stage_to_tier


def print_deployment_plan(plan: DeploymentPlan) -> None:
    """Print formatted deployment plan.

    Args:
        plan: DeploymentPlan to print
    """
    print(f"\n{'='*70}")
    print("DEPLOYMENT PLAN")
    print(f"{'='*70}")

    print(f"\nAvailable Capital: ${plan.available_capital:,.2f}")
    print(f"To Deploy: ${plan.total_deployed:,.2f}")
    print(f"Remaining: ${plan.remaining_cash:,.2f}")

    print(f"\nReasoning:")
    for reason in plan.reasoning:
        print(f"  • {reason}")

    if plan.recommendations:
        print(f"\n{'='*70}")
        print("RECOMMENDATIONS")
        print(f"{'='*70}")
        print(f"{'Ticker':<8} {'Amount':>10} {'Shares':>8} {'Tier':>6} {'Score':>7} {'Reason':<30}")
        print("-" * 70)

        for rec in plan.recommendations:
            tier_num = rec.tier.value.replace("tier_", "")
            score_str = f"{rec.score:.0f}" if rec.score else "N/A"
            print(
                f"{rec.ticker:<8} "
                f"${rec.amount:>8,.0f} "
                f"{rec.shares_estimate:>8.2f} "
                f"{tier_num:>6} "
                f"{score_str:>7} "
                f"{rec.reason[:30]:<30}"
            )

        print("-" * 70)
        print(f"{'TOTAL':<8} ${plan.total_deployed:>8,.0f}")

    print("=" * 70)
