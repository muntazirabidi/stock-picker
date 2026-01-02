"""Financial Modeling Prep API client with caching and rate limiting."""

import time
from pathlib import Path
from typing import Any

import requests
from pydantic import ValidationError
from pydantic_settings import BaseSettings
from tenacity import retry, stop_after_attempt, wait_exponential

from .cache import FileCache
from .models import (
    BalanceSheet,
    CashFlowStatement,
    CompanyFinancials,
    CompanyProfile,
    IncomeStatement,
    KeyMetrics,
    Quote,
)


class FMPSettings(BaseSettings):
    """FMP API configuration."""

    fmp_api_key: str
    fmp_base_url: str = "https://financialmodelingprep.com/api/v3"
    fmp_rate_limit_per_minute: int = 300  # Free tier is ~300/min

    class Config:
        env_file = ".env"
        extra = "ignore"


class FMPError(Exception):
    """FMP API error."""

    pass


class FMPClient:
    """Client for Financial Modeling Prep API.

    Features:
    - Automatic caching of responses
    - Rate limiting
    - Retry logic for transient failures
    - Pydantic model validation
    """

    def __init__(
        self,
        api_key: str | None = None,
        cache_dir: Path | None = None,
        cache_ttl_hours: int = 24,
    ):
        settings = FMPSettings()
        self.api_key = api_key or settings.fmp_api_key
        self.base_url = settings.fmp_base_url
        self.rate_limit = settings.fmp_rate_limit_per_minute

        self.cache = FileCache(cache_dir=cache_dir, ttl_hours=cache_ttl_hours)
        self._last_request_time = 0.0
        self._request_count = 0
        self._minute_start = time.time()

    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting."""
        now = time.time()

        # Reset counter every minute
        if now - self._minute_start > 60:
            self._request_count = 0
            self._minute_start = now

        # If we've hit the limit, wait
        if self._request_count >= self.rate_limit:
            sleep_time = 60 - (now - self._minute_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._request_count = 0
            self._minute_start = time.time()

        self._request_count += 1

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _request(
        self, endpoint: str, params: dict[str, Any] | None = None, use_cache: bool = True
    ) -> Any:
        """Make API request with caching and retry logic.

        Args:
            endpoint: API endpoint (e.g., "/profile/AAPL")
            params: Additional query parameters
            use_cache: Whether to use cache (default True)

        Returns:
            Parsed JSON response
        """
        params = params or {}
        params["apikey"] = self.api_key

        # Build cache key
        cache_key = f"{endpoint}:{sorted(params.items())}"

        # Check cache first
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        # Rate limit
        self._rate_limit_wait()

        # Make request
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 429:
            raise FMPError("Rate limit exceeded")

        if response.status_code != 200:
            raise FMPError(f"API error {response.status_code}: {response.text}")

        data = response.json()

        # Check for API error messages
        if isinstance(data, dict) and "Error Message" in data:
            raise FMPError(data["Error Message"])

        # Cache successful response
        if use_cache:
            self.cache.set(cache_key, data)

        return data

    # -------------------------------------------------------------------------
    # Profile & Quote endpoints
    # -------------------------------------------------------------------------

    def get_profile(self, ticker: str) -> CompanyProfile | None:
        """Get company profile.

        Args:
            ticker: Stock symbol

        Returns:
            CompanyProfile or None if not found
        """
        data = self._request(f"/profile/{ticker.upper()}")

        if not data or not isinstance(data, list) or len(data) == 0:
            return None

        try:
            return CompanyProfile.model_validate(data[0])
        except ValidationError:
            return None

    def get_quote(self, ticker: str) -> Quote | None:
        """Get current stock quote.

        Args:
            ticker: Stock symbol

        Returns:
            Quote or None if not found
        """
        data = self._request(f"/quote/{ticker.upper()}", use_cache=False)

        if not data or not isinstance(data, list) or len(data) == 0:
            return None

        try:
            return Quote.model_validate(data[0])
        except ValidationError:
            return None

    def get_batch_quotes(self, tickers: list[str]) -> dict[str, Quote]:
        """Get quotes for multiple tickers in one call.

        Args:
            tickers: List of stock symbols

        Returns:
            Dict mapping ticker to Quote
        """
        if not tickers:
            return {}

        # FMP supports comma-separated tickers
        ticker_str = ",".join(t.upper() for t in tickers)
        data = self._request(f"/quote/{ticker_str}", use_cache=False)

        if not data or not isinstance(data, list):
            return {}

        result = {}
        for item in data:
            try:
                quote = Quote.model_validate(item)
                result[quote.symbol] = quote
            except ValidationError:
                continue

        return result

    # -------------------------------------------------------------------------
    # Financial statements
    # -------------------------------------------------------------------------

    def get_income_statements(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[IncomeStatement]:
        """Get income statements.

        Args:
            ticker: Stock symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch

        Returns:
            List of IncomeStatement (newest first)
        """
        data = self._request(
            f"/income-statement/{ticker.upper()}",
            params={"period": period, "limit": limit},
        )

        if not data or not isinstance(data, list):
            return []

        result = []
        for item in data:
            try:
                result.append(IncomeStatement.model_validate(item))
            except ValidationError:
                continue

        return result

    def get_balance_sheets(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[BalanceSheet]:
        """Get balance sheets.

        Args:
            ticker: Stock symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch

        Returns:
            List of BalanceSheet (newest first)
        """
        data = self._request(
            f"/balance-sheet-statement/{ticker.upper()}",
            params={"period": period, "limit": limit},
        )

        if not data or not isinstance(data, list):
            return []

        result = []
        for item in data:
            try:
                result.append(BalanceSheet.model_validate(item))
            except ValidationError:
                continue

        return result

    def get_cash_flow_statements(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[CashFlowStatement]:
        """Get cash flow statements.

        Args:
            ticker: Stock symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch

        Returns:
            List of CashFlowStatement (newest first)
        """
        data = self._request(
            f"/cash-flow-statement/{ticker.upper()}",
            params={"period": period, "limit": limit},
        )

        if not data or not isinstance(data, list):
            return []

        result = []
        for item in data:
            try:
                result.append(CashFlowStatement.model_validate(item))
            except ValidationError:
                continue

        return result

    def get_key_metrics(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[KeyMetrics]:
        """Get key financial metrics.

        Args:
            ticker: Stock symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch

        Returns:
            List of KeyMetrics (newest first)
        """
        data = self._request(
            f"/key-metrics/{ticker.upper()}",
            params={"period": period, "limit": limit},
        )

        if not data or not isinstance(data, list):
            return []

        result = []
        for item in data:
            try:
                result.append(KeyMetrics.model_validate(item))
            except ValidationError:
                continue

        return result

    # -------------------------------------------------------------------------
    # Aggregated data
    # -------------------------------------------------------------------------

    def get_company_financials(
        self, ticker: str, years: int = 10, include_quote: bool = True
    ) -> CompanyFinancials | None:
        """Get all financial data for a company.

        Args:
            ticker: Stock symbol
            years: Years of historical data
            include_quote: Whether to fetch current quote

        Returns:
            CompanyFinancials or None if profile not found
        """
        ticker = ticker.upper()

        # Get profile first - if this fails, company doesn't exist
        profile = self.get_profile(ticker)
        if profile is None:
            return None

        # Fetch all financial data
        income = self.get_income_statements(ticker, limit=years)
        balance = self.get_balance_sheets(ticker, limit=years)
        cashflow = self.get_cash_flow_statements(ticker, limit=years)
        metrics = self.get_key_metrics(ticker, limit=years)
        quote = self.get_quote(ticker) if include_quote else None

        return CompanyFinancials(
            profile=profile,
            income_statements=income,
            balance_sheets=balance,
            cash_flows=cashflow,
            key_metrics=metrics,
            quote=quote,
        )

    # -------------------------------------------------------------------------
    # Universe / Index constituents
    # -------------------------------------------------------------------------

    def get_sp500_constituents(self) -> list[dict[str, Any]]:
        """Get S&P 500 constituents.

        Returns:
            List of dicts with symbol, name, sector, etc.
        """
        return self._request("/sp500_constituent") or []

    def get_nasdaq100_constituents(self) -> list[dict[str, Any]]:
        """Get Nasdaq 100 constituents.

        Returns:
            List of dicts with symbol, name, sector, etc.
        """
        return self._request("/nasdaq_constituent") or []

    def get_dowjones_constituents(self) -> list[dict[str, Any]]:
        """Get Dow Jones constituents.

        Returns:
            List of dicts with symbol, name, sector, etc.
        """
        return self._request("/dowjones_constituent") or []

    def stock_screener(
        self,
        market_cap_min: int | None = None,
        market_cap_max: int | None = None,
        sector: str | None = None,
        industry: str | None = None,
        exchange: str | None = None,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """Screen stocks by criteria.

        Args:
            market_cap_min: Minimum market cap
            market_cap_max: Maximum market cap
            sector: Filter by sector
            industry: Filter by industry
            exchange: Filter by exchange (NYSE, NASDAQ, etc.)
            limit: Max results

        Returns:
            List of matching stocks
        """
        params: dict[str, Any] = {"limit": limit}

        if market_cap_min:
            params["marketCapMoreThan"] = market_cap_min
        if market_cap_max:
            params["marketCapLowerThan"] = market_cap_max
        if sector:
            params["sector"] = sector
        if industry:
            params["industry"] = industry
        if exchange:
            params["exchange"] = exchange

        return self._request("/stock-screener", params=params) or []

    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for stocks by name or ticker.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of matching stocks
        """
        return self._request("/search", params={"query": query, "limit": limit}) or []

    def clear_cache(self) -> int:
        """Clear all cached data.

        Returns:
            Number of cache entries cleared
        """
        return self.cache.clear()

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self.cache.stats()
