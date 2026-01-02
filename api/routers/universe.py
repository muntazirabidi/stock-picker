"""Universe API router."""

from fastapi import APIRouter, HTTPException, Query
from typing import Literal

from api.schemas import CompanyScore, ScoreRequest

router = APIRouter()


@router.get("/tickers")
async def get_universe_tickers(
    type: Literal["sp500", "nasdaq100", "midcap", "smallcap", "all"] = Query("sp500")
) -> list[str]:
    """Get tickers for a specific universe."""
    try:
        from src.data.yahoo_client import YahooClient

        client = YahooClient()

        if type == "sp500":
            return client.get_sp500_tickers()
        elif type == "nasdaq100":
            return client.get_nasdaq100_tickers()
        elif type == "midcap":
            return client.get_sp400_midcap_tickers()
        elif type == "smallcap":
            return client.get_sp600_smallcap_tickers()
        elif type == "all":
            # Combine all S&P indices
            sp500 = set(client.get_sp500_tickers())
            sp400 = set(client.get_sp400_midcap_tickers())
            sp600 = set(client.get_sp600_smallcap_tickers())
            return list(sp500 | sp400 | sp600)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown universe type: {type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score")
async def score_universe(request: ScoreRequest) -> list[CompanyScore]:
    """Score a list of tickers."""
    try:
        from src.data.yahoo_client import YahooClient
        from src.metrics.calculator import MetricsCalculator
        from src.scoring.composite import UniverseScorer

        client = YahooClient()
        calculator = MetricsCalculator()
        scorer = UniverseScorer()

        # Calculate metrics for each ticker
        all_metrics = []
        for ticker in request.tickers:
            try:
                financials = client.get_company_financials(ticker)
                if financials:
                    metrics = calculator.calculate(financials)
                    if metrics:
                        all_metrics.append(metrics)
            except Exception:
                # Skip tickers that fail
                continue

        if not all_metrics:
            return []

        # Score the universe
        scores = scorer.score_universe(all_metrics)

        # Convert to response format
        return [
            CompanyScore(
                ticker=s.ticker,
                name=s.name,
                stage=s.stage,
                composite_score=s.composite_score,
                quality_score=s.quality_score,
                growth_score=s.growth_score,
                strength_score=s.strength_score,
                valuation_score=s.valuation_score,
            )
            for s in scores
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
