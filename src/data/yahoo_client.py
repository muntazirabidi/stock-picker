"""Yahoo Finance data client using yfinance library.

This is the primary free data source for the equity research system.
Provides company profiles, financials, and quotes without API key requirements.
"""

import io
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yfinance as yf
from pydantic import ValidationError

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


class YahooClient:
    """Client for Yahoo Finance data via yfinance.

    Features:
    - No API key required (free)
    - Automatic caching of responses
    - Rate limiting to avoid being blocked
    - Pydantic model validation
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        cache_ttl_hours: int = 24,
        requests_per_second: float = 2.0,
    ):
        self.cache = FileCache(cache_dir=cache_dir, ttl_hours=cache_ttl_hours)
        self._min_interval = 1.0 / requests_per_second
        self._last_request_time = 0.0

    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting to avoid being blocked."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """Get yfinance Ticker object with rate limiting."""
        self._rate_limit_wait()
        return yf.Ticker(symbol.upper())

    # -------------------------------------------------------------------------
    # Profile & Quote
    # -------------------------------------------------------------------------

    def get_profile(self, ticker: str) -> CompanyProfile | None:
        """Get company profile.

        Args:
            ticker: Stock symbol

        Returns:
            CompanyProfile or None if not found
        """
        cache_key = f"profile:{ticker.upper()}"
        cached = self.cache.get(cache_key)
        if cached:
            try:
                return CompanyProfile.model_validate(cached)
            except ValidationError:
                pass

        try:
            t = self._get_ticker(ticker)
            info = t.info

            if not info or "symbol" not in info:
                return None

            profile_data = {
                "symbol": info.get("symbol", ticker.upper()),
                "companyName": info.get("longName") or info.get("shortName", ""),
                "exchange": info.get("exchange"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "mktCap": info.get("marketCap"),
                "description": info.get("longBusinessSummary"),
                "country": info.get("country"),
                "isEtf": info.get("quoteType") == "ETF",
                "isActivelyTrading": True,
            }

            self.cache.set(cache_key, profile_data)
            return CompanyProfile.model_validate(profile_data)

        except Exception:
            return None

    def get_quote(self, ticker: str) -> Quote | None:
        """Get current stock quote.

        Args:
            ticker: Stock symbol

        Returns:
            Quote or None if not found
        """
        try:
            t = self._get_ticker(ticker)
            info = t.info

            if not info or "symbol" not in info:
                return None

            quote_data = {
                "symbol": info.get("symbol", ticker.upper()),
                "price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
                "marketCap": info.get("marketCap"),
                "volume": info.get("volume"),
                "avgVolume": info.get("averageVolume"),
                "change": info.get("regularMarketChange"),
                "changesPercentage": info.get("regularMarketChangePercent"),
                "yearHigh": info.get("fiftyTwoWeekHigh"),
                "yearLow": info.get("fiftyTwoWeekLow"),
                "pe": info.get("trailingPE"),
                "eps": info.get("trailingEps"),
            }

            return Quote.model_validate(quote_data)

        except Exception:
            return None

    def get_batch_quotes(self, tickers: list[str]) -> dict[str, Quote]:
        """Get quotes for multiple tickers.

        Args:
            tickers: List of stock symbols

        Returns:
            Dict mapping ticker to Quote
        """
        result = {}
        for ticker in tickers:
            quote = self.get_quote(ticker)
            if quote:
                result[ticker.upper()] = quote
        return result

    # -------------------------------------------------------------------------
    # Financial Statements
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
        cache_key = f"income:{ticker.upper()}:{period}:{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            result = []
            for item in cached:
                try:
                    result.append(IncomeStatement.model_validate(item))
                except ValidationError:
                    continue
            if result:
                return result

        try:
            t = self._get_ticker(ticker)
            if period == "annual":
                df = t.financials
            else:
                df = t.quarterly_financials

            if df is None or df.empty:
                return []

            # Transpose: columns become rows (dates)
            df = df.T
            statements = []

            for idx, row in df.head(limit).iterrows():
                stmt_date = idx
                if isinstance(stmt_date, pd.Timestamp):
                    stmt_date = stmt_date.date()
                elif isinstance(stmt_date, datetime):
                    stmt_date = stmt_date.date()

                stmt_data = {
                    "date": stmt_date,
                    "symbol": ticker.upper(),
                    "period": "FY" if period == "annual" else "Q",
                    "revenue": self._safe_get(row, "Total Revenue"),
                    "grossProfit": self._safe_get(row, "Gross Profit"),
                    "operatingIncome": self._safe_get(row, "Operating Income"),
                    "netIncome": self._safe_get(row, "Net Income"),
                    "ebitda": self._safe_get(row, "EBITDA"),
                    "researchAndDevelopmentExpenses": self._safe_get(
                        row, "Research Development"
                    ),
                    "sellingGeneralAndAdministrativeExpenses": self._safe_get(
                        row, "Selling General Administrative"
                    ),
                }

                # Calculate ratios if we have revenue
                revenue = stmt_data.get("revenue")
                if revenue and revenue > 0:
                    if stmt_data.get("grossProfit"):
                        stmt_data["grossProfitRatio"] = stmt_data["grossProfit"] / revenue
                    if stmt_data.get("operatingIncome"):
                        stmt_data["operatingIncomeRatio"] = (
                            stmt_data["operatingIncome"] / revenue
                        )
                    if stmt_data.get("netIncome"):
                        stmt_data["netIncomeRatio"] = stmt_data["netIncome"] / revenue

                try:
                    statements.append(IncomeStatement.model_validate(stmt_data))
                except ValidationError:
                    continue

            # Cache raw data
            cache_data = [
                {
                    "date": str(s.date),
                    "symbol": s.symbol,
                    "period": s.period,
                    "revenue": s.revenue,
                    "grossProfit": s.gross_profit,
                    "operatingIncome": s.operating_income,
                    "netIncome": s.net_income,
                    "ebitda": s.ebitda,
                    "grossProfitRatio": s.gross_profit_ratio,
                    "operatingIncomeRatio": s.operating_income_ratio,
                    "netIncomeRatio": s.net_income_ratio,
                }
                for s in statements
            ]
            self.cache.set(cache_key, cache_data)

            return statements

        except Exception:
            return []

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
        cache_key = f"balance:{ticker.upper()}:{period}:{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            result = []
            for item in cached:
                try:
                    result.append(BalanceSheet.model_validate(item))
                except ValidationError:
                    continue
            if result:
                return result

        try:
            t = self._get_ticker(ticker)
            if period == "annual":
                df = t.balance_sheet
            else:
                df = t.quarterly_balance_sheet

            if df is None or df.empty:
                return []

            df = df.T
            sheets = []

            for idx, row in df.head(limit).iterrows():
                stmt_date = idx
                if isinstance(stmt_date, pd.Timestamp):
                    stmt_date = stmt_date.date()
                elif isinstance(stmt_date, datetime):
                    stmt_date = stmt_date.date()

                sheet_data = {
                    "date": stmt_date,
                    "symbol": ticker.upper(),
                    "period": "FY" if period == "annual" else "Q",
                    "totalAssets": self._safe_get(row, "Total Assets"),
                    "totalCurrentAssets": self._safe_get(row, "Total Current Assets"),
                    "cashAndCashEquivalents": self._safe_get(
                        row, "Cash And Cash Equivalents"
                    ),
                    "shortTermInvestments": self._safe_get(row, "Short Term Investments"),
                    "inventory": self._safe_get(row, "Inventory"),
                    "netReceivables": self._safe_get(row, "Net Receivables"),
                    "totalLiabilities": self._safe_get(
                        row, "Total Liabilities Net Minority Interest"
                    ),
                    "totalCurrentLiabilities": self._safe_get(
                        row, "Total Current Liabilities"
                    ),
                    "totalDebt": self._safe_get(row, "Total Debt"),
                    "longTermDebt": self._safe_get(row, "Long Term Debt"),
                    "shortTermDebt": self._safe_get(row, "Short Term Debt"),
                    "totalStockholdersEquity": self._safe_get(
                        row, "Total Stockholders Equity"
                    ),
                    "retainedEarnings": self._safe_get(row, "Retained Earnings"),
                    "commonStockSharesOutstanding": self._safe_get(
                        row, "Share Issued"
                    ),
                }

                try:
                    sheets.append(BalanceSheet.model_validate(sheet_data))
                except ValidationError:
                    continue

            # Cache
            cache_data = [
                {
                    "date": str(s.date),
                    "symbol": s.symbol,
                    "period": s.period,
                    "totalAssets": s.total_assets,
                    "totalCurrentAssets": s.total_current_assets,
                    "cashAndCashEquivalents": s.cash_and_equivalents,
                    "totalLiabilities": s.total_liabilities,
                    "totalStockholdersEquity": s.total_equity,
                    "totalDebt": s.total_debt,
                }
                for s in sheets
            ]
            self.cache.set(cache_key, cache_data)

            return sheets

        except Exception:
            return []

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
        cache_key = f"cashflow:{ticker.upper()}:{period}:{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            result = []
            for item in cached:
                try:
                    result.append(CashFlowStatement.model_validate(item))
                except ValidationError:
                    continue
            if result:
                return result

        try:
            t = self._get_ticker(ticker)
            if period == "annual":
                df = t.cashflow
            else:
                df = t.quarterly_cashflow

            if df is None or df.empty:
                return []

            df = df.T
            flows = []

            for idx, row in df.head(limit).iterrows():
                stmt_date = idx
                if isinstance(stmt_date, pd.Timestamp):
                    stmt_date = stmt_date.date()
                elif isinstance(stmt_date, datetime):
                    stmt_date = stmt_date.date()

                ocf = self._safe_get(row, "Operating Cash Flow")
                capex = self._safe_get(row, "Capital Expenditure")
                fcf = None
                if ocf is not None and capex is not None:
                    fcf = ocf + capex  # capex is usually negative

                flow_data = {
                    "date": stmt_date,
                    "symbol": ticker.upper(),
                    "period": "FY" if period == "annual" else "Q",
                    "operatingCashFlow": ocf,
                    "netIncome": self._safe_get(row, "Net Income"),
                    "depreciationAndAmortization": self._safe_get(
                        row, "Depreciation And Amortization"
                    ),
                    "stockBasedCompensation": self._safe_get(
                        row, "Stock Based Compensation"
                    ),
                    "capitalExpenditure": capex,
                    "freeCashFlow": fcf or self._safe_get(row, "Free Cash Flow"),
                    "dividendsPaid": self._safe_get(row, "Dividends Paid"),
                    "commonStockRepurchased": self._safe_get(
                        row, "Repurchase Of Capital Stock"
                    ),
                    "commonStockIssued": self._safe_get(row, "Issuance Of Capital Stock"),
                }

                try:
                    flows.append(CashFlowStatement.model_validate(flow_data))
                except ValidationError:
                    continue

            # Cache
            cache_data = [
                {
                    "date": str(s.date),
                    "symbol": s.symbol,
                    "period": s.period,
                    "operatingCashFlow": s.operating_cash_flow,
                    "freeCashFlow": s.free_cash_flow,
                    "capitalExpenditure": s.capital_expenditure,
                    "stockBasedCompensation": s.stock_based_compensation,
                }
                for s in flows
            ]
            self.cache.set(cache_key, cache_data)

            return flows

        except Exception:
            return []

    def get_key_metrics(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[KeyMetrics]:
        """Get key financial metrics.

        Note: yfinance doesn't provide historical metrics, so we calculate
        from financial statements or return current metrics only.

        Args:
            ticker: Stock symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch

        Returns:
            List of KeyMetrics (usually just current/TTM)
        """
        cache_key = f"metrics:{ticker.upper()}"
        cached = self.cache.get(cache_key)
        if cached:
            try:
                return [KeyMetrics.model_validate(cached)]
            except ValidationError:
                pass

        try:
            t = self._get_ticker(ticker)
            info = t.info

            if not info:
                return []

            metrics_data = {
                "date": date.today(),
                "symbol": ticker.upper(),
                "period": "TTM",
                "peRatio": info.get("trailingPE"),
                "priceToSalesRatio": info.get("priceToSalesTrailing12Months"),
                "pbRatio": info.get("priceToBook"),
                "enterpriseValueOverEBITDA": info.get("enterpriseToEbitda"),
                "evToSales": info.get("enterpriseToRevenue"),
                "roe": info.get("returnOnEquity"),
                "roic": None,  # Not directly available
                "revenuePerShare": info.get("revenuePerShare"),
                "bookValuePerShare": info.get("bookValue"),
                "dividendYield": info.get("dividendYield"),
                "freeCashFlowYield": None,
                "earningsYield": (
                    1 / info["trailingPE"] if info.get("trailingPE") else None
                ),
                "currentRatio": info.get("currentRatio"),
                "debtToEquity": info.get("debtToEquity"),
                "pegRatio": info.get("pegRatio"),
            }

            # Cache
            cache_data = {**metrics_data, "date": str(metrics_data["date"])}
            self.cache.set(cache_key, cache_data)

            return [KeyMetrics.model_validate(metrics_data)]

        except Exception:
            return []

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

        profile = self.get_profile(ticker)
        if profile is None:
            return None

        income = self.get_income_statements(ticker, limit=years)
        balance = self.get_balance_sheets(ticker, limit=years)
        cashflow = self.get_cash_flow_statements(ticker, limit=years)
        metrics = self.get_key_metrics(ticker)
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
    # Universe loading helpers
    # -------------------------------------------------------------------------

    def _fetch_wikipedia_table(self, url: str) -> list[pd.DataFrame]:
        """Fetch tables from Wikipedia with proper headers.

        Args:
            url: Wikipedia URL to fetch

        Returns:
            List of DataFrames parsed from HTML tables
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return pd.read_html(io.StringIO(response.text))

    def get_sp500_tickers(self) -> list[str]:
        """Get S&P 500 ticker list from Wikipedia.

        Returns:
            List of ticker symbols
        """
        cache_key = "universe:sp500"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = self._fetch_wikipedia_table(url)
            df = tables[0]
            tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
            self.cache.set(cache_key, tickers)
            return tickers
        except Exception:
            return []

    def get_nasdaq100_tickers(self) -> list[str]:
        """Get Nasdaq 100 ticker list from Wikipedia.

        Returns:
            List of ticker symbols
        """
        cache_key = "universe:nasdaq100"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            tables = self._fetch_wikipedia_table(url)
            # Find the table with tickers
            for table in tables:
                if "Ticker" in table.columns:
                    tickers = table["Ticker"].tolist()
                    self.cache.set(cache_key, tickers)
                    return tickers
                elif "Symbol" in table.columns:
                    tickers = table["Symbol"].tolist()
                    self.cache.set(cache_key, tickers)
                    return tickers
            return []
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    def _safe_get(self, row: pd.Series, key: str) -> float | None:
        """Safely get a value from a pandas Series."""
        try:
            val = row.get(key)
            if pd.isna(val):
                return None
            return float(val)
        except (KeyError, TypeError, ValueError):
            return None

    def clear_cache(self) -> int:
        """Clear all cached data."""
        return self.cache.clear()

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self.cache.stats()
