"""Company API router."""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from typing import Literal

from api.schemas import (
    CompanyProfile,
    CompanyFinancials,
    CompanyMetrics,
    CompanyScore,
    PriceBar,
    NewsArticle,
    Quote,
    IncomeStatement,
    QualityMetrics,
    GrowthMetrics,
    StrengthMetrics,
    ValuationMetrics,
    StageClassification,
)

router = APIRouter()


def get_client():
    """Get Yahoo Finance client."""
    from src.data.yahoo_client import YahooClient
    return YahooClient()


@router.get("/{ticker}/profile")
async def get_company_profile(ticker: str) -> CompanyProfile:
    """Get company profile."""
    try:
        client = get_client()
        profile = client.get_profile(ticker.upper())

        if not profile:
            raise HTTPException(status_code=404, detail=f"Company not found: {ticker}")

        return CompanyProfile(
            symbol=profile.symbol,
            company_name=profile.company_name,
            exchange=profile.exchange or "",
            sector=profile.sector or "",
            industry=profile.industry or "",
            market_cap=profile.market_cap or 0,
            description=profile.description or "",
            country=profile.country or "",
            is_etf=profile.is_etf,
            is_actively_trading=profile.is_actively_trading,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/financials")
async def get_company_financials(ticker: str) -> CompanyFinancials:
    """Get company financials including profile, quote, and statements."""
    try:
        client = get_client()
        financials = client.get_company_financials(ticker.upper())

        if not financials:
            raise HTTPException(status_code=404, detail=f"Financials not found: {ticker}")

        return CompanyFinancials(
            profile=CompanyProfile(
                symbol=financials.profile.symbol,
                company_name=financials.profile.company_name,
                exchange=financials.profile.exchange or "",
                sector=financials.profile.sector or "",
                industry=financials.profile.industry or "",
                market_cap=financials.profile.market_cap or 0,
                description=financials.profile.description or "",
                country=financials.profile.country or "",
                is_etf=financials.profile.is_etf,
                is_actively_trading=financials.profile.is_actively_trading,
            ),
            quote=Quote(
                symbol=financials.quote.symbol,
                price=financials.quote.price,
                market_cap=financials.quote.market_cap,
                volume=financials.quote.volume,
                change=financials.quote.change,
                change_percent=financials.quote.change_percent,
                year_high=financials.quote.year_high,
                year_low=financials.quote.year_low,
                pe=financials.quote.pe,
                eps=financials.quote.eps,
            ),
            income_statements=[
                IncomeStatement(
                    date=stmt.date,
                    revenue=stmt.revenue,
                    gross_profit=stmt.gross_profit,
                    operating_income=stmt.operating_income,
                    net_income=stmt.net_income,
                    ebitda=stmt.ebitda or 0,
                    eps=stmt.eps or 0,
                )
                for stmt in financials.income_statements
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/metrics")
async def get_company_metrics(ticker: str) -> CompanyMetrics:
    """Get calculated metrics for a company."""
    try:
        from src.metrics.calculator import MetricsCalculator

        client = get_client()
        financials = client.get_company_financials(ticker.upper())

        if not financials:
            raise HTTPException(status_code=404, detail=f"Financials not found: {ticker}")

        calculator = MetricsCalculator()
        metrics = calculator.calculate(financials)

        if not metrics:
            raise HTTPException(status_code=500, detail="Failed to calculate metrics")

        # Extract traditional metrics if available
        quality = QualityMetrics()
        growth = GrowthMetrics()
        strength = StrengthMetrics()
        valuation = ValuationMetrics()

        if metrics.traditional:
            t = metrics.traditional
            quality = QualityMetrics(
                roic=t.quality.roic,
                roe=t.quality.roe,
                roa=t.quality.roa,
                gross_margin=t.quality.gross_margin,
                operating_margin=t.quality.operating_margin,
                net_margin=t.quality.net_margin,
                fcf_margin=t.quality.fcf_margin,
                asset_turnover=t.quality.asset_turnover,
            )
            growth = GrowthMetrics(
                revenue_growth_1y=t.growth.revenue_growth_1y,
                revenue_cagr_3y=t.growth.revenue_cagr_3y,
                revenue_cagr_5y=t.growth.revenue_cagr_5y,
                earnings_growth_1y=t.growth.earnings_growth_1y,
                earnings_cagr_3y=t.growth.earnings_cagr_3y,
                fcf_growth_1y=t.growth.fcf_growth_1y,
                fcf_cagr_3y=t.growth.fcf_cagr_3y,
            )
            strength = StrengthMetrics(
                current_ratio=t.strength.current_ratio,
                quick_ratio=t.strength.quick_ratio,
                debt_to_equity=t.strength.debt_to_equity,
                interest_coverage=t.strength.interest_coverage,
            )
            valuation = ValuationMetrics(
                pe_ratio=t.valuation.pe_ratio,
                ps_ratio=t.valuation.ps_ratio,
                pb_ratio=t.valuation.pb_ratio,
                ev_ebitda=t.valuation.ev_ebitda,
                ev_sales=t.valuation.ev_sales,
                fcf_yield=t.valuation.fcf_yield,
                earnings_yield=t.valuation.earnings_yield,
                peg_ratio=t.valuation.peg_ratio,
            )

        return CompanyMetrics(
            ticker=metrics.ticker,
            name=metrics.name,
            stage=StageClassification(
                stage=metrics.stage.stage.value,
                confidence=metrics.stage.confidence,
                reasons=metrics.stage.reasons,
            ),
            quality=quality,
            growth=growth,
            strength=strength,
            valuation=valuation,
            market_cap=metrics.market_cap or 0,
            current_price=metrics.current_price or 0,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/score")
async def get_company_score(ticker: str) -> CompanyScore:
    """Get composite score for a company."""
    try:
        from src.metrics.calculator import MetricsCalculator
        from src.scoring.composite import UniverseScorer

        client = get_client()
        financials = client.get_company_financials(ticker.upper())

        if not financials:
            raise HTTPException(status_code=404, detail=f"Financials not found: {ticker}")

        calculator = MetricsCalculator()
        metrics = calculator.calculate(financials)

        if not metrics:
            raise HTTPException(status_code=500, detail="Failed to calculate metrics")

        scorer = UniverseScorer()
        scores = scorer.score_universe([metrics])

        if not scores:
            raise HTTPException(status_code=500, detail="Failed to calculate score")

        s = scores[0]
        return CompanyScore(
            ticker=s.ticker,
            name=s.name,
            stage=s.stage,
            composite_score=s.composite_score,
            quality_score=s.quality_score,
            growth_score=s.growth_score,
            strength_score=s.strength_score,
            valuation_score=s.valuation_score,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/price-history")
async def get_price_history(
    ticker: str,
    period: Literal["1M", "1Y", "2Y", "5Y"] = Query("1Y")
) -> list[PriceBar]:
    """Get historical price data."""
    try:
        import yfinance as yf

        # Calculate date range
        end_date = datetime.now()
        if period == "1M":
            start_date = end_date - timedelta(days=30)
        elif period == "1Y":
            start_date = end_date - timedelta(days=365)
        elif period == "2Y":
            start_date = end_date - timedelta(days=730)
        else:  # 5Y
            start_date = end_date - timedelta(days=1825)

        # Fetch data
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            return []

        return [
            PriceBar(
                date=idx.strftime("%Y-%m-%d"),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"]),
            )
            for idx, row in hist.iterrows()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/news")
async def get_company_news(ticker: str, limit: int = Query(10, ge=1, le=50)) -> list[NewsArticle]:
    """Get recent news for a company."""
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker.upper())
        news = stock.news or []

        return [
            NewsArticle(
                title=article.get("title", ""),
                url=article.get("link", ""),
                publisher=article.get("publisher", ""),
                published_at=datetime.fromtimestamp(
                    article.get("providerPublishTime", 0)
                ).isoformat(),
                summary=article.get("summary"),
            )
            for article in news[:limit]
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
