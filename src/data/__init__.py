"""Data layer for equity research system."""

from .cache import FileCache
from .fmp_client import FMPClient, FMPError
from .models import (
    BalanceSheet,
    CashFlowStatement,
    CompanyFinancials,
    CompanyProfile,
    CompanyStage,
    Holding,
    IncomeStatement,
    KeyMetrics,
    Quote,
    Tier,
    UniverseStock,
)
from .universe import UniverseLoader, get_universe_summary
from .yahoo_client import YahooClient

__all__ = [
    # Cache
    "FileCache",
    # Data Clients
    "YahooClient",  # Primary (free)
    "FMPClient",  # Requires paid subscription
    "FMPError",
    # Models
    "BalanceSheet",
    "CashFlowStatement",
    "CompanyFinancials",
    "CompanyProfile",
    "CompanyStage",
    "Holding",
    "IncomeStatement",
    "KeyMetrics",
    "Quote",
    "Tier",
    "UniverseStock",
    # Universe
    "UniverseLoader",
    "get_universe_summary",
]
