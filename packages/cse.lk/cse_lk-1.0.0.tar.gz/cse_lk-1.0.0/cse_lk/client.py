"""Main CSE API client implementation."""

import requests
import time
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

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
    CSEAPIError,
    CSENetworkError,
    CSEValidationError,
    CSERateLimitError,
)


class CSEClient:
    """
    Client for accessing the Colombo Stock Exchange (CSE) API.

    This client provides methods to access all available CSE API endpoints
    with proper error handling, rate limiting, and response parsing.

    Example:
        >>> client = CSEClient()
        >>> company_info = client.get_company_info("LOLC.N0000")
        >>> print(f"{company_info.name}: {company_info.last_traded_price}")
        L O L C HOLDINGS PLC: 546.5
    """

    BASE_URL = "https://www.cse.lk/api/"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(
        self,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        Initialize the CSE API client.

        Args:
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
            retry_delay: Delay between retries in seconds (default: 1)
            session: Optional requests session to use
        """
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.MAX_RETRIES
        self.retry_delay = retry_delay or self.RETRY_DELAY
        self.session = session or requests.Session()

        # Set default headers
        self.session.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "cse.lk-python-client/1.0.0",
            }
        )

    def _make_request(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make a POST request to the CSE API with retry logic.

        Args:
            endpoint: API endpoint path
            data: Request data dictionary

        Returns:
            Response data as dictionary or list

        Raises:
            CSENetworkError: For network-related errors
            CSEAPIError: For API error responses
            CSERateLimitError: For rate limiting errors
        """
        url = urljoin(self.BASE_URL, endpoint)
        data = data or {}

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.post(url, data=data, timeout=self.timeout)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(
                        response.headers.get("Retry-After", self.retry_delay)
                    )
                    raise CSERateLimitError(
                        f"Rate limit exceeded. Retry after {retry_after} seconds.",
                        retry_after=retry_after,
                    )

                # Handle other HTTP errors
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                    except ValueError:
                        error_data = {"error": response.text}

                    raise CSEAPIError(
                        f"API request failed with status {response.status_code}: "
                        f"{response.text}",
                        status_code=response.status_code,
                        response_data=error_data,
                    )

                # Parse JSON response
                try:
                    json_response = response.json()
                    return json_response
                except ValueError as e:
                    raise CSEAPIError(f"Invalid JSON response: {e}")

            except requests.exceptions.Timeout as e:
                last_exception = CSENetworkError(f"Request timeout: {e}")
            except requests.exceptions.ConnectionError as e:
                last_exception = CSENetworkError(f"Connection error: {e}")
            except requests.exceptions.RequestException as e:
                last_exception = CSENetworkError(f"Request error: {e}")
            except (CSEAPIError, CSERateLimitError):
                # Don't retry API errors or rate limit errors
                raise

            # Wait before retrying
            if attempt < self.max_retries:
                time.sleep(self.retry_delay * (2**attempt))  # Exponential backoff

        # If we got here, all retries failed
        if last_exception:
            raise last_exception
        raise CSENetworkError("Maximum retries exceeded")

    def _validate_symbol(self, symbol: str) -> str:
        """
        Validate and normalize a stock symbol.

        Args:
            symbol: Stock symbol to validate

        Returns:
            Normalized symbol

        Raises:
            CSEValidationError: If symbol is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise CSEValidationError("Symbol must be a non-empty string")

        symbol = symbol.strip().upper()
        if not symbol:
            raise CSEValidationError("Symbol cannot be empty")

        return symbol

    def _make_dict_request(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request expecting a dictionary response."""
        if data is not None:
            response = self._make_request(endpoint, data)
        else:
            response = self._make_request(endpoint)
        if not isinstance(response, dict):
            raise CSEAPIError(
                f"Expected dictionary response from {endpoint}, got {type(response)}"
            )
        return response

    def _make_list_request(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Make a request expecting a list response."""
        if data is not None:
            response = self._make_request(endpoint, data)
        else:
            response = self._make_request(endpoint)
        if not isinstance(response, list):
            raise CSEAPIError(
                f"Expected list response from {endpoint}, got {type(response)}"
            )
        return response

    # Market Data Methods

    def get_company_info(self, symbol: str) -> CompanyInfo:
        """
        Get detailed information for a specific company/security.

        Args:
            symbol: Stock symbol (e.g., "LOLC.N0000")

        Returns:
            CompanyInfo object with detailed company information

        Raises:
            CSEValidationError: If symbol is invalid
            CSEAPIError: If API request fails
        """
        symbol = self._validate_symbol(symbol)
        data = {"symbol": symbol}
        response = self._make_dict_request("companyInfoSummery", data)
        return CompanyInfo.from_dict(response)

    def get_trade_summary(self) -> List[TradeSummary]:
        """
        Get trade summary for all securities.

        Returns:
            List of TradeSummary objects
        """
        response = self._make_dict_request("tradeSummary")
        trade_summaries = response.get("reqTradeSummery", [])
        return [TradeSummary.from_dict(item) for item in trade_summaries]

    def get_today_share_prices(self) -> List[SharePrice]:
        """
        Get today's share price data for all securities.

        Returns:
            List of SharePrice objects
        """
        response = self._make_list_request("todaySharePrice")
        return [SharePrice.from_dict(item) for item in response]

    def get_top_gainers(self) -> List[TopGainer]:
        """
        Get list of top gaining stocks.

        Returns:
            List of TopGainer objects
        """
        response = self._make_list_request("topGainers")
        return [TopGainer.from_dict(item) for item in response]

    def get_top_losers(self) -> List[TopLoser]:
        """
        Get list of top losing stocks.

        Returns:
            List of TopLoser objects
        """
        response = self._make_list_request("topLooses")
        return [TopLoser.from_dict(item) for item in response]

    def get_most_active_trades(self) -> List[ActiveTrade]:
        """
        Get most active trades by volume.

        Returns:
            List of ActiveTrade objects
        """
        response = self._make_list_request("mostActiveTrades")
        return [ActiveTrade.from_dict(item) for item in response]

    def get_market_status(self) -> MarketStatus:
        """
        Get current market status (open/closed).

        Returns:
            MarketStatus object
        """
        response = self._make_dict_request("marketStatus")
        return MarketStatus.from_dict(response)

    def get_market_summary(self) -> MarketSummary:
        """
        Get market summary data.

        Returns:
            MarketSummary object
        """
        response = self._make_dict_request("marketSummery")
        return MarketSummary.from_dict(response)

    def get_aspi_data(self) -> IndexData:
        """
        Get All Share Price Index (ASPI) data.

        Returns:
            IndexData object with ASPI information
        """
        response = self._make_dict_request("aspiData")
        return IndexData.from_dict(response)

    def get_snp_data(self) -> IndexData:
        """
        Get S&P Sri Lanka 20 Index data.

        Returns:
            IndexData object with S&P SL20 information
        """
        response = self._make_dict_request("snpData")
        return IndexData.from_dict(response)

    def get_chart_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get chart data for a specific stock.

        Note: This endpoint may return HTTP 400 for some symbols.

        Args:
            symbol: Stock symbol

        Returns:
            Raw chart data dictionary
        """
        symbol = self._validate_symbol(symbol)
        data = {"symbol": symbol}
        return self._make_dict_request("chartData", data)

    def get_all_sectors(self) -> List[Sector]:
        """
        Get data for all sectors.

        Returns:
            List of Sector objects
        """
        response = self._make_list_request("allSectors")
        return [Sector.from_dict(item) for item in response]

    def get_detailed_trades(self, symbol: Optional[str] = None) -> List[DetailedTrade]:
        """
        Get detailed trade information.

        Args:
            symbol: Optional stock symbol to filter by

        Returns:
            List of DetailedTrade objects
        """
        data = {}
        if symbol:
            data["symbol"] = self._validate_symbol(symbol)

        response = self._make_dict_request("detailedTrades", data)
        detailed_trades = response.get("reqDetailTrades", [])
        return [DetailedTrade.from_dict(item) for item in detailed_trades]

    def get_daily_market_summary(self) -> List[DailyMarketSummary]:
        """
        Get daily market summary data.

        Returns:
            List of DailyMarketSummary objects
        """
        response = self._make_list_request("dailyMarketSummery")
        # Response is nested list format
        if response and isinstance(response[0], list):
            return [DailyMarketSummary.from_dict(item) for item in response[0]]
        return []

    # Announcement Methods

    def get_new_listings_announcements(self) -> List[Announcement]:
        """
        Get new listings and related announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("getNewListingsRelatedNoticesAnnouncements")
        announcements = response.get("newListingRelatedAnnouncements", [])
        return [Announcement.from_dict(item) for item in announcements]

    def get_buy_in_board_announcements(self) -> List[Announcement]:
        """
        Get buy-in board announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("getBuyInBoardAnnouncements")
        announcements = response.get("buyInBoardAnnouncements", [])
        return [Announcement.from_dict(item) for item in announcements]

    def get_approved_announcements(self) -> List[Announcement]:
        """
        Get approved announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("approvedAnnouncement")
        announcements = response.get("approvedAnnouncements", [])
        return [Announcement.from_dict(item) for item in announcements]

    def get_covid_announcements(self) -> List[Announcement]:
        """
        Get COVID-related announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("getCOVIDAnnouncements")
        announcements = response.get("covidAnnouncements", [])
        return [Announcement.from_dict(item) for item in announcements]

    def get_financial_announcements(self) -> List[Announcement]:
        """
        Get financial announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("getFinancialAnnouncement")
        announcements = response.get("reqFinancialAnnouncemnets", [])
        return [Announcement.from_dict(item) for item in announcements]

    def get_circular_announcements(self) -> List[Announcement]:
        """
        Get circular announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("circularAnnouncement")
        announcements = response.get("reqCircularAnnouncement", [])
        return [Announcement.from_dict(item) for item in announcements]

    def get_directive_announcements(self) -> List[Announcement]:
        """
        Get directive announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("directiveAnnouncement")
        announcements = response.get("reqDirectiveAnnouncement", [])
        return [Announcement.from_dict(item) for item in announcements]

    def get_non_compliance_announcements(self) -> List[Announcement]:
        """
        Get non-compliance announcements.

        Returns:
            List of Announcement objects
        """
        response = self._make_dict_request("getNonComplianceAnnouncements")
        announcements = response.get("nonComplianceAnnouncements", [])
        return [Announcement.from_dict(item) for item in announcements]

    # Convenience Methods

    def search_companies(self, query: str) -> List[SharePrice]:
        """
        Search for companies by name or symbol.

        This is a convenience method that filters today's share prices
        by the given query string.

        Args:
            query: Search term (case-insensitive)

        Returns:
            List of SharePrice objects matching the query
        """
        if not query:
            raise CSEValidationError("Query cannot be empty")

        query = query.lower().strip()
        all_prices = self.get_today_share_prices()

        return [price for price in all_prices if query in price.symbol.lower()]

    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get a comprehensive market overview.

        Returns:
            Dictionary containing market status, summary, and key indices
        """
        return {
            "status": self.get_market_status(),
            "summary": self.get_market_summary(),
            "aspi": self.get_aspi_data(),
            "snp_sl20": self.get_snp_data(),
            "top_gainers": self.get_top_gainers()[:5],  # Top 5
            "top_losers": self.get_top_losers()[:5],  # Top 5
            "most_active": self.get_most_active_trades()[:5],  # Top 5
        }

    def __enter__(self) -> "CSEClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.session.close()
