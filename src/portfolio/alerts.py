"""Portfolio alerts and monitoring.

Generates alerts for:
- Score changes (thesis review needed)
- Position size warnings
- Allocation drift
- Loss thresholds
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Sequence

from src.data.models import Tier
from src.scoring import CompanyScore

from .allocation import AllocationSummary


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts."""

    SCORE_DROP = "score_drop"
    SCORE_IMPROVEMENT = "score_improvement"
    POSITION_OVERSIZED = "position_oversized"
    TIER_UNDERWEIGHT = "tier_underweight"
    TIER_OVERWEIGHT = "tier_overweight"
    SIGNIFICANT_LOSS = "significant_loss"
    SIGNIFICANT_GAIN = "significant_gain"
    NEW_TOP_PICK = "new_top_pick"


@dataclass
class Alert:
    """Portfolio alert."""

    alert_type: AlertType
    severity: AlertSeverity
    ticker: str | None
    message: str
    details: str | None = None
    action_suggested: str | None = None
    created_date: date = None

    def __post_init__(self):
        if self.created_date is None:
            self.created_date = date.today()


class AlertGenerator:
    """Generates portfolio alerts."""

    def __init__(
        self,
        score_drop_threshold: float = 10.0,  # Points drop to trigger alert
        score_improvement_threshold: float = 15.0,  # Points gain to highlight
        loss_threshold: float = -0.15,  # 15% loss
        gain_threshold: float = 0.50,  # 50% gain
        position_warning_pct: float = 1.2,  # 20% over max position size
    ):
        """Initialize alert generator.

        Args:
            score_drop_threshold: Score points drop to trigger alert
            score_improvement_threshold: Score points improvement to highlight
            loss_threshold: Loss percentage to trigger alert
            gain_threshold: Gain percentage to highlight (consider trimming)
            position_warning_pct: Multiple of max position size to warn
        """
        self.score_drop_threshold = score_drop_threshold
        self.score_improvement_threshold = score_improvement_threshold
        self.loss_threshold = loss_threshold
        self.gain_threshold = gain_threshold
        self.position_warning_pct = position_warning_pct

    def check_score_changes(
        self,
        current_scores: Sequence[CompanyScore],
        previous_scores: dict[str, float],  # ticker -> previous score
        held_tickers: set[str],
    ) -> list[Alert]:
        """Check for significant score changes in held positions.

        Args:
            current_scores: Current scored universe
            previous_scores: Previous scores by ticker
            held_tickers: Set of currently held tickers

        Returns:
            List of alerts
        """
        alerts: list[Alert] = []

        for score in current_scores:
            if score.ticker not in held_tickers:
                continue

            if score.composite_score is None:
                continue

            prev_score = previous_scores.get(score.ticker)
            if prev_score is None:
                continue

            change = score.composite_score - prev_score

            if change <= -self.score_drop_threshold:
                alerts.append(
                    Alert(
                        alert_type=AlertType.SCORE_DROP,
                        severity=AlertSeverity.WARNING,
                        ticker=score.ticker,
                        message=f"{score.ticker} score dropped {abs(change):.0f} points",
                        details=f"Previous: {prev_score:.0f} → Current: {score.composite_score:.0f}",
                        action_suggested="Review investment thesis",
                    )
                )
            elif change >= self.score_improvement_threshold:
                alerts.append(
                    Alert(
                        alert_type=AlertType.SCORE_IMPROVEMENT,
                        severity=AlertSeverity.INFO,
                        ticker=score.ticker,
                        message=f"{score.ticker} score improved {change:.0f} points",
                        details=f"Previous: {prev_score:.0f} → Current: {score.composite_score:.0f}",
                        action_suggested="Consider adding to position",
                    )
                )

        return alerts

    def check_allocation(self, allocation: AllocationSummary) -> list[Alert]:
        """Check for allocation issues.

        Args:
            allocation: Current allocation summary

        Returns:
            List of alerts
        """
        alerts: list[Alert] = []

        # Check tier allocations
        for tier, tier_alloc in allocation.tier_allocations.items():
            tier_name = tier.value.replace("tier_", "Tier ")

            if tier_alloc.is_underweight and abs(tier_alloc.difference_pct) > 0.05:
                alerts.append(
                    Alert(
                        alert_type=AlertType.TIER_UNDERWEIGHT,
                        severity=AlertSeverity.WARNING,
                        ticker=None,
                        message=f"{tier_name} significantly underweight",
                        details=f"Target: {tier_alloc.target_pct*100:.0f}% | Actual: {tier_alloc.actual_pct*100:.0f}%",
                        action_suggested=f"Consider adding {tier_name} positions",
                    )
                )
            elif tier_alloc.is_overweight and tier_alloc.difference_pct > 0.10:
                alerts.append(
                    Alert(
                        alert_type=AlertType.TIER_OVERWEIGHT,
                        severity=AlertSeverity.INFO,
                        ticker=None,
                        message=f"{tier_name} significantly overweight",
                        details=f"Target: {tier_alloc.target_pct*100:.0f}% | Actual: {tier_alloc.actual_pct*100:.0f}%",
                        action_suggested="Consider rebalancing or letting new capital catch up",
                    )
                )

        # Check position sizes
        for pos in allocation.position_allocations:
            if pos.weight_pct > pos.max_position_pct * self.position_warning_pct:
                alerts.append(
                    Alert(
                        alert_type=AlertType.POSITION_OVERSIZED,
                        severity=AlertSeverity.WARNING,
                        ticker=pos.ticker,
                        message=f"{pos.ticker} exceeds max position size",
                        details=f"Current: {pos.weight_pct*100:.1f}% | Max: {pos.max_position_pct*100:.1f}%",
                        action_suggested="Consider trimming position",
                    )
                )

            # Check for significant losses
            if pos.gain_loss_pct <= self.loss_threshold:
                alerts.append(
                    Alert(
                        alert_type=AlertType.SIGNIFICANT_LOSS,
                        severity=AlertSeverity.WARNING,
                        ticker=pos.ticker,
                        message=f"{pos.ticker} down {abs(pos.gain_loss_pct)*100:.0f}%",
                        details=f"Cost: ${pos.cost_basis:,.0f} | Current: ${pos.current_value:,.0f}",
                        action_suggested="Review thesis - is it still valid?",
                    )
                )

            # Check for significant gains (tax/rebalancing consideration)
            if pos.gain_loss_pct >= self.gain_threshold:
                alerts.append(
                    Alert(
                        alert_type=AlertType.SIGNIFICANT_GAIN,
                        severity=AlertSeverity.INFO,
                        ticker=pos.ticker,
                        message=f"{pos.ticker} up {pos.gain_loss_pct*100:.0f}%",
                        details=f"Cost: ${pos.cost_basis:,.0f} | Current: ${pos.current_value:,.0f}",
                        action_suggested="Consider taking some profits if overweight",
                    )
                )

        return alerts

    def check_new_opportunities(
        self,
        scores: Sequence[CompanyScore],
        held_tickers: set[str],
        top_n: int = 5,
        min_score: float = 70.0,
    ) -> list[Alert]:
        """Check for high-scoring stocks not currently held.

        Args:
            scores: Scored universe
            held_tickers: Currently held tickers
            top_n: Number of top picks to highlight
            min_score: Minimum score to consider

        Returns:
            List of alerts
        """
        alerts: list[Alert] = []

        # Filter to unheld stocks with good scores
        candidates = [
            s for s in scores
            if s.ticker not in held_tickers
            and s.composite_score is not None
            and s.composite_score >= min_score
        ]

        # Sort by score
        candidates.sort(key=lambda s: s.composite_score or 0, reverse=True)

        for score in candidates[:top_n]:
            alerts.append(
                Alert(
                    alert_type=AlertType.NEW_TOP_PICK,
                    severity=AlertSeverity.INFO,
                    ticker=score.ticker,
                    message=f"{score.ticker} is a top-scoring stock you don't own",
                    details=f"Score: {score.composite_score:.0f} | Stage: {score.stage.value}",
                    action_suggested="Research for potential addition",
                )
            )

        return alerts

    def generate_all_alerts(
        self,
        allocation: AllocationSummary,
        current_scores: Sequence[CompanyScore],
        previous_scores: dict[str, float] | None = None,
    ) -> list[Alert]:
        """Generate all relevant alerts.

        Args:
            allocation: Current allocation summary
            current_scores: Current scored universe
            previous_scores: Optional previous scores for change detection

        Returns:
            List of all alerts, sorted by severity
        """
        held_tickers = {pos.ticker for pos in allocation.position_allocations}

        alerts: list[Alert] = []

        # Allocation alerts
        alerts.extend(self.check_allocation(allocation))

        # Score change alerts
        if previous_scores:
            alerts.extend(
                self.check_score_changes(current_scores, previous_scores, held_tickers)
            )

        # New opportunity alerts
        alerts.extend(self.check_new_opportunities(current_scores, held_tickers))

        # Sort by severity (critical first, then warning, then info)
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.INFO: 2,
        }
        alerts.sort(key=lambda a: severity_order[a.severity])

        return alerts


def print_alerts(alerts: Sequence[Alert]) -> None:
    """Print formatted alerts.

    Args:
        alerts: List of alerts to print
    """
    if not alerts:
        print("\n✓ No alerts - portfolio looks healthy!")
        return

    print(f"\n{'='*70}")
    print(f"PORTFOLIO ALERTS ({len(alerts)} items)")
    print(f"{'='*70}")

    # Group by severity
    by_severity: dict[AlertSeverity, list[Alert]] = {
        AlertSeverity.CRITICAL: [],
        AlertSeverity.WARNING: [],
        AlertSeverity.INFO: [],
    }

    for alert in alerts:
        by_severity[alert.severity].append(alert)

    # Print critical first
    if by_severity[AlertSeverity.CRITICAL]:
        print("\n🚨 CRITICAL:")
        for alert in by_severity[AlertSeverity.CRITICAL]:
            _print_single_alert(alert)

    if by_severity[AlertSeverity.WARNING]:
        print("\n⚠️  WARNINGS:")
        for alert in by_severity[AlertSeverity.WARNING]:
            _print_single_alert(alert)

    if by_severity[AlertSeverity.INFO]:
        print("\nℹ️  INFO:")
        for alert in by_severity[AlertSeverity.INFO]:
            _print_single_alert(alert)

    print("=" * 70)


def _print_single_alert(alert: Alert) -> None:
    """Print a single alert."""
    ticker_str = f"[{alert.ticker}] " if alert.ticker else ""
    print(f"  {ticker_str}{alert.message}")
    if alert.details:
        print(f"    {alert.details}")
    if alert.action_suggested:
        print(f"    → {alert.action_suggested}")
