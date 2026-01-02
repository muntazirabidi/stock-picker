"""Universe API router."""

from fastapi import APIRouter, HTTPException, Query
from typing import Literal

from api.schemas import CompanyScore, CompanyScoreWithValuation, ScoreRequest

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
    import logging
    logger = logging.getLogger(__name__)

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
                logger.info(f"Fetching financials for {ticker}")
                financials = client.get_company_financials(ticker)
                if financials:
                    metrics = calculator.calculate(financials)
                    if metrics:
                        all_metrics.append(metrics)
                        logger.info(f"Successfully processed {ticker}")
            except Exception as e:
                logger.warning(f"Failed to process {ticker}: {e}")
                continue

        if not all_metrics:
            logger.warning("No metrics calculated for any ticker")
            return []

        # Score the universe
        logger.info(f"Scoring {len(all_metrics)} companies")
        scores = scorer.score_universe(all_metrics)

        # Convert to response format, filtering out entries with None scores
        result = []
        for s in scores:
            # Skip if any required score is None
            if any(v is None for v in [s.composite_score, s.quality_score, s.growth_score, s.strength_score, s.valuation_score]):
                logger.warning(f"Skipping {s.ticker} due to None scores")
                continue
            result.append(CompanyScore(
                ticker=s.ticker,
                name=s.name,
                stage=s.stage,
                composite_score=s.composite_score,
                quality_score=s.quality_score,
                growth_score=s.growth_score,
                strength_score=s.strength_score,
                valuation_score=s.valuation_score,
            ))
        return result
    except Exception as e:
        logger.error(f"Score universe error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score-with-valuation")
async def score_universe_with_valuation(request: ScoreRequest) -> list[CompanyScoreWithValuation]:
    """Score tickers with detailed valuation metrics for value investing."""
    import logging
    logger = logging.getLogger(__name__)

    try:
        from src.data.yahoo_client import YahooClient
        from src.metrics.calculator import MetricsCalculator
        from src.scoring.composite import UniverseScorer

        client = YahooClient()
        calculator = MetricsCalculator()
        scorer = UniverseScorer()

        # Calculate metrics for each ticker, store raw metrics too
        all_metrics = []
        metrics_map = {}  # ticker -> raw metrics for valuation data

        for ticker in request.tickers:
            try:
                logger.info(f"Fetching financials for {ticker}")
                financials = client.get_company_financials(ticker)
                if financials:
                    metrics = calculator.calculate(financials)
                    if metrics:
                        all_metrics.append(metrics)
                        metrics_map[ticker] = metrics
                        logger.info(f"Successfully processed {ticker}")
            except Exception as e:
                logger.warning(f"Failed to process {ticker}: {e}")
                continue

        if not all_metrics:
            logger.warning("No metrics calculated for any ticker")
            return []

        # Score the universe
        logger.info(f"Scoring {len(all_metrics)} companies")
        scores = scorer.score_universe(all_metrics)

        # Convert to response format with valuation details
        result = []
        for s in scores:
            # Skip if any required score is None
            if any(v is None for v in [s.composite_score, s.quality_score, s.growth_score, s.strength_score, s.valuation_score]):
                logger.warning(f"Skipping {s.ticker} due to None scores")
                continue

            # Get raw metrics for this ticker
            raw = metrics_map.get(s.ticker)
            valuation = raw.valuation if raw else None

            # Calculate value score: 50% quality + 50% valuation
            value_score = (s.quality_score + s.valuation_score) / 2 if s.quality_score and s.valuation_score else None

            result.append(CompanyScoreWithValuation(
                ticker=s.ticker,
                name=s.name,
                sector=raw.sector if raw else None,
                stage=s.stage,
                composite_score=s.composite_score,
                quality_score=s.quality_score,
                growth_score=s.growth_score,
                strength_score=s.strength_score,
                valuation_score=s.valuation_score,
                pe_ratio=valuation.pe_ratio if valuation else None,
                peg_ratio=valuation.peg_ratio if valuation else None,
                ps_ratio=valuation.ps_ratio if valuation else None,
                pb_ratio=valuation.pb_ratio if valuation else None,
                ev_ebitda=valuation.ev_to_ebitda if valuation else None,
                fcf_yield=valuation.fcf_yield if valuation else None,
                earnings_yield=valuation.earnings_yield if valuation else None,
                value_score=value_score,
                market_cap=raw.market_cap if raw else None,
            ))

        # Sort by value_score descending (best value picks first)
        result.sort(key=lambda x: x.value_score or 0, reverse=True)
        return result

    except Exception as e:
        logger.error(f"Score universe with valuation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
