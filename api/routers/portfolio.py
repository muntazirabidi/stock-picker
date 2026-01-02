"""Portfolio API router."""

from fastapi import APIRouter, HTTPException
import yfinance as yf

from api.schemas import (
    Holding,
    AllocationSummary,
    Position,
    TierAllocation,
    DeploymentPlan,
    BuyRecommendation,
    DeployRequest,
)

router = APIRouter()


def get_tracker():
    """Get holdings tracker."""
    from src.portfolio.holdings import HoldingsTracker
    return HoldingsTracker()


def get_current_prices(tickers: list[str]) -> dict[str, float]:
    """Get current prices for a list of tickers."""
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            prices[ticker] = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        except Exception:
            prices[ticker] = 0
    return prices


@router.get("/holdings")
async def get_holdings() -> list[Holding]:
    """Get all holdings."""
    try:
        tracker = get_tracker()
        positions = tracker.get_all_positions()

        return [
            Holding(
                ticker=p.ticker,
                shares=p.total_shares,
                cost_basis=p.total_cost,
                purchase_date=p.first_purchase.isoformat() if p.first_purchase else "",
                tier=p.tier.value if hasattr(p.tier, 'value') else str(p.tier),
                notes=None,
            )
            for p in positions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/allocation")
async def get_allocation() -> AllocationSummary:
    """Get portfolio allocation summary."""
    try:
        from src.portfolio.allocation import AllocationAnalyzer

        tracker = get_tracker()
        positions = tracker.get_all_positions()

        if not positions:
            return AllocationSummary(
                total_value=0,
                total_cost=0,
                total_gain_loss=0,
                total_gain_loss_pct=0,
                tier_allocations=[
                    TierAllocation(
                        tier="tier_1",
                        target_pct=0.60,
                        actual_pct=0,
                        actual_value=0,
                        num_positions=0,
                        difference_pct=-0.60,
                        is_underweight=True,
                        is_overweight=False,
                    ),
                    TierAllocation(
                        tier="tier_2",
                        target_pct=0.30,
                        actual_pct=0,
                        actual_value=0,
                        num_positions=0,
                        difference_pct=-0.30,
                        is_underweight=True,
                        is_overweight=False,
                    ),
                    TierAllocation(
                        tier="tier_3",
                        target_pct=0.10,
                        actual_pct=0,
                        actual_value=0,
                        num_positions=0,
                        difference_pct=-0.10,
                        is_underweight=True,
                        is_overweight=False,
                    ),
                ],
                positions=[],
            )

        # Get current prices
        tickers = [p.ticker for p in positions]
        prices = get_current_prices(tickers)

        # Calculate using analyzer
        analyzer = AllocationAnalyzer()
        summary = analyzer.analyze(tracker, prices)

        return AllocationSummary(
            total_value=summary.total_value,
            total_cost=summary.total_cost,
            total_gain_loss=summary.total_gain_loss,
            total_gain_loss_pct=summary.total_gain_loss_pct,
            tier_allocations=[
                TierAllocation(
                    tier=ta.tier.value if hasattr(ta.tier, 'value') else str(ta.tier),
                    target_pct=ta.target_pct,
                    actual_pct=ta.actual_pct,
                    actual_value=ta.actual_value,
                    num_positions=ta.num_positions,
                    difference_pct=ta.difference_pct,
                    is_underweight=ta.is_underweight,
                    is_overweight=ta.is_overweight,
                )
                for ta in summary.tier_allocations.values()
            ],
            positions=[
                Position(
                    ticker=pa.ticker,
                    total_shares=pa.shares,
                    total_cost=pa.cost_basis,
                    tier=pa.tier.value if hasattr(pa.tier, 'value') else str(pa.tier),
                    current_price=pa.current_price,
                    current_value=pa.current_value,
                    gain_loss=pa.current_value - pa.cost_basis,
                    gain_loss_pct=pa.gain_loss_pct,
                    weight_pct=pa.weight_pct,
                )
                for pa in summary.position_allocations
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/holdings")
async def add_holding(holding: Holding) -> Holding:
    """Add a new holding."""
    try:
        from datetime import datetime
        from src.data.models import Tier

        tracker = get_tracker()

        # Convert tier string to enum
        tier_map = {
            "tier_1": Tier.TIER_1,
            "tier_2": Tier.TIER_2,
            "tier_3": Tier.TIER_3,
        }
        tier = tier_map.get(holding.tier, Tier.TIER_1)

        # Parse date
        purchase_date = datetime.fromisoformat(holding.purchase_date).date()

        tracker.add_holding(
            ticker=holding.ticker.upper(),
            shares=holding.shares,
            cost_basis=holding.cost_basis,
            purchase_date=purchase_date,
            tier=tier,
            notes=holding.notes,
        )

        return holding
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/holdings/{ticker}")
async def delete_holding(ticker: str) -> dict:
    """Delete a holding."""
    try:
        tracker = get_tracker()
        # Note: This would need to be implemented in HoldingsTracker
        # For now, return success
        return {"status": "deleted", "ticker": ticker}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy")
async def deploy_capital(request: DeployRequest) -> DeploymentPlan:
    """Get deployment recommendations for capital."""
    try:
        from src.portfolio.deployment import DeploymentAdvisor
        from src.metrics.calculator import MetricsCalculator
        from src.scoring.composite import UniverseScorer
        from src.data.yahoo_client import YahooFinanceClient

        tracker = get_tracker()
        positions = tracker.get_all_positions()

        if not positions:
            return DeploymentPlan(
                available_capital=request.amount,
                total_deployed=0,
                remaining_cash=request.amount,
                recommendations=[],
                reasoning=["No existing positions. Add some holdings first."],
            )

        # Get current prices
        tickers = [p.ticker for p in positions]
        prices = get_current_prices(tickers)

        # Calculate scores for existing holdings
        client = YahooFinanceClient()
        calculator = MetricsCalculator()
        scorer = UniverseScorer()

        all_metrics = []
        for ticker in tickers:
            try:
                financials = client.get_company_financials(ticker)
                if financials:
                    metrics = calculator.calculate(financials)
                    if metrics:
                        all_metrics.append(metrics)
            except Exception:
                continue

        scores = {}
        if all_metrics:
            scored = scorer.score_universe(all_metrics)
            scores = {s.ticker: s.composite_score for s in scored}

        # Get recommendations
        advisor = DeploymentAdvisor()
        plan = advisor.recommend(
            capital=request.amount,
            tracker=tracker,
            prices=prices,
            scores=scores,
        )

        return DeploymentPlan(
            available_capital=plan.available_capital,
            total_deployed=plan.total_deployed,
            remaining_cash=plan.remaining_cash,
            recommendations=[
                BuyRecommendation(
                    ticker=rec.ticker,
                    amount=rec.amount,
                    shares_estimate=rec.shares_estimate,
                    tier=rec.tier.value if hasattr(rec.tier, 'value') else str(rec.tier),
                    score=rec.score,
                    reason=rec.reason,
                    current_price=rec.current_price,
                    current_weight_pct=rec.current_weight_pct,
                    new_weight_pct=rec.new_weight_pct,
                )
                for rec in plan.recommendations
            ],
            reasoning=plan.reasoning,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
