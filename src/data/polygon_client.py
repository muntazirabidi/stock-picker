"""Polygon.io / Massive API client for market data.

Provides historical prices, technical indicators, news, and real-time quotes.
"""

import os
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

from .cache import FileCache

load_dotenv()


@dataclass
class PriceBar:
    """OHLCV price bar."""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float | None = None


@dataclass
class TechnicalIndicator:
    """Technical indicator value."""
    date: date
    value: float


@dataclass
class NewsArticle:
    """News article."""
    id: str
    title: str
    author: str | None
    published: datetime
    article_url: str
    tickers: list[str]
    description: str | None = None
    image_url: str | None = None
    publisher_name: str | None = None


@dataclass
class TickerSnapshot:
    """Current ticker snapshot."""
    ticker: str
    price: float
    change: float
    change_pct: float
    volume: int
    vwap: float | None
    open: float | None
    high: float | None
    low: float | None
    prev_close: float | None


class PolygonClient:
    """Client for Polygon.io / Massive API.

    Features:
    - Historical OHLCV data (daily, hourly, minute)
    - Technical indicators (SMA, EMA, RSI, MACD)
    - News feed
    - Real-time snapshots
    - Automatic caching
    - Rate limiting
    """

    BASE_URL = "https://api.polygon.io"

    def __init__(
        self,
        api_key: str | None = None,
        cache_dir: Path | None = None,
        cache_ttl_hours: int = 1,  # Short TTL for price data
        requests_per_second: float = 5.0,
    ):
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY not set")

        self.cache = FileCache(cache_dir=cache_dir, ttl_hours=cache_ttl_hours)
        self._min_interval = 1.0 / requests_per_second
        self._last_request_time = 0.0
        self._session = requests.Session()

    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _request(self, endpoint: str, params: dict | None = None) -> dict | None:
        """Make authenticated API request."""
        self._rate_limit_wait()

        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key

        try:
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    # -------------------------------------------------------------------------
    # Historical Price Data
    # -------------------------------------------------------------------------

    def get_daily_bars(
        self,
        ticker: str,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 365,
    ) -> list[PriceBar]:
        """Get daily OHLCV bars.

        Args:
            ticker: Stock symbol
            start_date: Start date (default: 1 year ago)
            end_date: End date (default: today)
            limit: Max bars to return

        Returns:
            List of PriceBar (oldest first)
        """
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=limit)

        cache_key = f"bars:daily:{ticker}:{start_date}:{end_date}"
        cached = self.cache.get(cache_key)
        if cached:
            return [PriceBar(**bar) for bar in cached]

        endpoint = f"/v2/aggs/ticker/{ticker.upper()}/range/1/day/{start_date}/{end_date}"
        data = self._request(endpoint, {"adjusted": "true", "sort": "asc", "limit": limit})

        if not data or "results" not in data:
            return []

        bars = []
        for r in data["results"]:
            bar_date = datetime.fromtimestamp(r["t"] / 1000).date()
            bars.append(PriceBar(
                date=bar_date,
                open=r["o"],
                high=r["h"],
                low=r["l"],
                close=r["c"],
                volume=r["v"],
                vwap=r.get("vw"),
            ))

        # Cache
        cache_data = [
            {"date": str(b.date), "open": b.open, "high": b.high, "low": b.low,
             "close": b.close, "volume": b.volume, "vwap": b.vwap}
            for b in bars
        ]
        self.cache.set(cache_key, cache_data)

        return bars

    def get_intraday_bars(
        self,
        ticker: str,
        timespan: str = "hour",  # minute, hour
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 100,
    ) -> list[PriceBar]:
        """Get intraday OHLCV bars.

        Args:
            ticker: Stock symbol
            timespan: "minute" or "hour"
            start_date: Start date
            end_date: End date
            limit: Max bars

        Returns:
            List of PriceBar
        """
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=7)

        endpoint = f"/v2/aggs/ticker/{ticker.upper()}/range/1/{timespan}/{start_date}/{end_date}"
        data = self._request(endpoint, {"adjusted": "true", "sort": "asc", "limit": limit})

        if not data or "results" not in data:
            return []

        bars = []
        for r in data["results"]:
            bar_date = datetime.fromtimestamp(r["t"] / 1000).date()
            bars.append(PriceBar(
                date=bar_date,
                open=r["o"],
                high=r["h"],
                low=r["l"],
                close=r["c"],
                volume=r["v"],
                vwap=r.get("vw"),
            ))

        return bars

    # -------------------------------------------------------------------------
    # Technical Indicators
    # -------------------------------------------------------------------------

    def get_sma(
        self,
        ticker: str,
        window: int = 50,
        timespan: str = "day",
        limit: int = 100,
    ) -> list[TechnicalIndicator]:
        """Get Simple Moving Average.

        Args:
            ticker: Stock symbol
            window: SMA period (e.g., 20, 50, 200)
            timespan: "day", "week", "month"
            limit: Number of data points

        Returns:
            List of TechnicalIndicator
        """
        cache_key = f"sma:{ticker}:{window}:{timespan}"
        cached = self.cache.get(cache_key)
        if cached:
            return [TechnicalIndicator(date=datetime.strptime(i["date"], "%Y-%m-%d").date(), value=i["value"]) for i in cached]

        endpoint = f"/v1/indicators/sma/{ticker.upper()}"
        data = self._request(endpoint, {
            "timespan": timespan,
            "window": window,
            "series_type": "close",
            "order": "asc",
            "limit": limit,
        })

        if not data or "results" not in data or "values" not in data["results"]:
            return []

        indicators = []
        for v in data["results"]["values"]:
            ind_date = datetime.fromtimestamp(v["timestamp"] / 1000).date()
            indicators.append(TechnicalIndicator(date=ind_date, value=v["value"]))

        cache_data = [{"date": str(i.date), "value": i.value} for i in indicators]
        self.cache.set(cache_key, cache_data)

        return indicators

    def get_ema(
        self,
        ticker: str,
        window: int = 20,
        timespan: str = "day",
        limit: int = 100,
    ) -> list[TechnicalIndicator]:
        """Get Exponential Moving Average."""
        endpoint = f"/v1/indicators/ema/{ticker.upper()}"
        data = self._request(endpoint, {
            "timespan": timespan,
            "window": window,
            "series_type": "close",
            "order": "asc",
            "limit": limit,
        })

        if not data or "results" not in data or "values" not in data["results"]:
            return []

        indicators = []
        for v in data["results"]["values"]:
            ind_date = datetime.fromtimestamp(v["timestamp"] / 1000).date()
            indicators.append(TechnicalIndicator(date=ind_date, value=v["value"]))

        return indicators

    def get_rsi(
        self,
        ticker: str,
        window: int = 14,
        timespan: str = "day",
        limit: int = 100,
    ) -> list[TechnicalIndicator]:
        """Get Relative Strength Index."""
        cache_key = f"rsi:{ticker}:{window}:{timespan}"
        cached = self.cache.get(cache_key)
        if cached:
            return [TechnicalIndicator(date=datetime.strptime(i["date"], "%Y-%m-%d").date(), value=i["value"]) for i in cached]

        endpoint = f"/v1/indicators/rsi/{ticker.upper()}"
        data = self._request(endpoint, {
            "timespan": timespan,
            "window": window,
            "series_type": "close",
            "order": "asc",
            "limit": limit,
        })

        if not data or "results" not in data or "values" not in data["results"]:
            return []

        indicators = []
        for v in data["results"]["values"]:
            ind_date = datetime.fromtimestamp(v["timestamp"] / 1000).date()
            indicators.append(TechnicalIndicator(date=ind_date, value=v["value"]))

        cache_data = [{"date": str(i.date), "value": i.value} for i in indicators]
        self.cache.set(cache_key, cache_data)

        return indicators

    def get_macd(
        self,
        ticker: str,
        short_window: int = 12,
        long_window: int = 26,
        signal_window: int = 9,
        timespan: str = "day",
        limit: int = 100,
    ) -> list[dict]:
        """Get MACD indicator.

        Returns:
            List of dicts with keys: date, value, signal, histogram
        """
        endpoint = f"/v1/indicators/macd/{ticker.upper()}"
        data = self._request(endpoint, {
            "timespan": timespan,
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
            "series_type": "close",
            "order": "asc",
            "limit": limit,
        })

        if not data or "results" not in data or "values" not in data["results"]:
            return []

        indicators = []
        for v in data["results"]["values"]:
            ind_date = datetime.fromtimestamp(v["timestamp"] / 1000).date()
            indicators.append({
                "date": ind_date,
                "value": v.get("value"),
                "signal": v.get("signal"),
                "histogram": v.get("histogram"),
            })

        return indicators

    # -------------------------------------------------------------------------
    # News
    # -------------------------------------------------------------------------

    def get_news(
        self,
        ticker: str | None = None,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """Get news articles.

        Args:
            ticker: Stock symbol (optional, for ticker-specific news)
            limit: Number of articles

        Returns:
            List of NewsArticle
        """
        params = {"limit": limit, "order": "desc"}
        if ticker:
            params["ticker"] = ticker.upper()

        data = self._request("/v2/reference/news", params)

        if not data or "results" not in data:
            return []

        articles = []
        for r in data["results"]:
            try:
                published = datetime.fromisoformat(r["published_utc"].replace("Z", "+00:00"))
            except (ValueError, KeyError):
                published = datetime.now()

            articles.append(NewsArticle(
                id=r.get("id", ""),
                title=r.get("title", ""),
                author=r.get("author"),
                published=published,
                article_url=r.get("article_url", ""),
                tickers=r.get("tickers", []),
                description=r.get("description"),
                image_url=r.get("image_url"),
                publisher_name=r.get("publisher", {}).get("name"),
            ))

        return articles

    # -------------------------------------------------------------------------
    # Snapshots / Real-time
    # -------------------------------------------------------------------------

    def get_snapshot(self, ticker: str) -> TickerSnapshot | None:
        """Get current ticker snapshot.

        Args:
            ticker: Stock symbol

        Returns:
            TickerSnapshot or None
        """
        data = self._request(f"/v2/snapshot/locale/us/markets/stocks/tickers/{ticker.upper()}")

        if not data or "ticker" not in data:
            return None

        t = data["ticker"]
        day = t.get("day", {})
        prev = t.get("prevDay", {})

        price = day.get("c") or t.get("lastTrade", {}).get("p", 0)
        prev_close = prev.get("c", price)
        change = price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0

        return TickerSnapshot(
            ticker=t.get("ticker", ticker.upper()),
            price=price,
            change=change,
            change_pct=change_pct,
            volume=day.get("v", 0),
            vwap=day.get("vw"),
            open=day.get("o"),
            high=day.get("h"),
            low=day.get("l"),
            prev_close=prev_close,
        )

    def get_top_movers(self, direction: str = "gainers") -> list[TickerSnapshot]:
        """Get top market movers.

        Args:
            direction: "gainers" or "losers"

        Returns:
            List of TickerSnapshot
        """
        data = self._request(f"/v2/snapshot/locale/us/markets/stocks/{direction}")

        if not data or "tickers" not in data:
            return []

        movers = []
        for t in data["tickers"][:20]:
            day = t.get("day", {})
            prev = t.get("prevDay", {})

            price = day.get("c", 0)
            prev_close = prev.get("c", price)
            change = price - prev_close
            change_pct = t.get("todaysChangePerc", 0)

            movers.append(TickerSnapshot(
                ticker=t.get("ticker", ""),
                price=price,
                change=change,
                change_pct=change_pct,
                volume=day.get("v", 0),
                vwap=day.get("vw"),
                open=day.get("o"),
                high=day.get("h"),
                low=day.get("l"),
                prev_close=prev_close,
            ))

        return movers

    # -------------------------------------------------------------------------
    # Previous Day
    # -------------------------------------------------------------------------

    def get_previous_close(self, ticker: str) -> PriceBar | None:
        """Get previous day's OHLCV data.

        Args:
            ticker: Stock symbol

        Returns:
            PriceBar or None
        """
        data = self._request(f"/v2/aggs/ticker/{ticker.upper()}/prev")

        if not data or "results" not in data or not data["results"]:
            return None

        r = data["results"][0]
        bar_date = datetime.fromtimestamp(r["t"] / 1000).date()

        return PriceBar(
            date=bar_date,
            open=r["o"],
            high=r["h"],
            low=r["l"],
            close=r["c"],
            volume=r["v"],
            vwap=r.get("vw"),
        )
