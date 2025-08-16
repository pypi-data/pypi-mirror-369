"""
CSE.LK - Colombo Stock Exchange API Client
==========================================

A comprehensive Python client for accessing the Colombo Stock Exchange (CSE) API.

Basic Usage:
    >>> from cse_lk import CSEClient
    >>> client = CSEClient()
    >>> company_info = client.get_company_info("LOLC.N0000")
    >>> print(company_info.name)
    'L O L C HOLDINGS PLC'

Features:
    - Complete API coverage for all CSE endpoints
    - Type-safe data models with proper validation
    - Comprehensive error handling
    - Rate limiting and retry mechanisms
    - Extensive documentation and examples

Author: CSE API Client Team
License: MIT
"""

from .client import CSEClient
from .models import (
    CompanyInfo,
    TradeSummary,
    SharePrice,
    TopGainer,
    TopLoser,
    ActiveTrade,
    MarketStatus,
    MarketSummary,
    IndexData,
    Sector,
    DetailedTrade,
    DailyMarketSummary,
    Announcement,
)
from .exceptions import (
    CSEError,
    CSEAPIError,
    CSENetworkError,
    CSEValidationError,
    CSEAuthenticationError,
    CSERateLimitError,
)

__version__ = "1.0.0"
__author__ = "CSE API Client Team"
__email__ = "contact@example.com"

__all__ = [
    # Main client
    "CSEClient",
    # Data models
    "CompanyInfo",
    "TradeSummary",
    "SharePrice",
    "TopGainer",
    "TopLoser",
    "ActiveTrade",
    "MarketStatus",
    "MarketSummary",
    "IndexData",
    "Sector",
    "DetailedTrade",
    "DailyMarketSummary",
    "Announcement",
    # Exceptions
    "CSEError",
    "CSEAPIError",
    "CSENetworkError",
    "CSEValidationError",
    "CSEAuthenticationError",
    "CSERateLimitError",
]
