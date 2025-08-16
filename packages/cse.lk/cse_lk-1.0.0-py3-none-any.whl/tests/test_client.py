"""Unit tests for the CSE client."""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import ConnectionError, Timeout

from cse_lk import CSEClient
from cse_lk.exceptions import (
    CSEAPIError,
    CSENetworkError,
    CSEValidationError,
    CSERateLimitError,
)
from cse_lk.models import CompanyInfo, MarketStatus, IndexData


class TestCSEClient:
    """Test cases for CSEClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = CSEClient()

    def test_init_default_values(self):
        """Test client initialization with default values."""
        client = CSEClient()
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.retry_delay == 1
        assert client.BASE_URL == "https://www.cse.lk/api/"

    def test_init_custom_values(self):
        """Test client initialization with custom values."""
        client = CSEClient(timeout=60, max_retries=5, retry_delay=2.0)
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    def test_validate_symbol_valid(self):
        """Test symbol validation with valid symbols."""
        assert self.client._validate_symbol("LOLC.N0000") == "LOLC.N0000"
        assert self.client._validate_symbol("  abc.x0000  ") == "ABC.X0000"

    def test_validate_symbol_invalid(self):
        """Test symbol validation with invalid symbols."""
        with pytest.raises(CSEValidationError):
            self.client._validate_symbol("")

        with pytest.raises(CSEValidationError):
            self.client._validate_symbol("   ")

        with pytest.raises(CSEValidationError):
            self.client._validate_symbol(None)

        with pytest.raises(CSEValidationError):
            self.client._validate_symbol(123)

    @patch("cse_lk.client.requests.Session.post")
    def test_make_request_success(self, mock_post):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_post.return_value = mock_response

        result = self.client._make_request("test_endpoint", {"param": "value"})

        assert result == {"test": "data"}
        mock_post.assert_called_once()

    @patch("cse_lk.client.requests.Session.post")
    def test_make_request_rate_limit(self, mock_post):
        """Test rate limit handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_post.return_value = mock_response

        with pytest.raises(CSERateLimitError) as exc_info:
            self.client._make_request("test_endpoint")

        assert exc_info.value.retry_after == 60

    @patch("cse_lk.client.requests.Session.post")
    def test_make_request_api_error(self, mock_post):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {"error": "Invalid parameter"}
        mock_post.return_value = mock_response

        with pytest.raises(CSEAPIError) as exc_info:
            self.client._make_request("test_endpoint")

        assert exc_info.value.status_code == 400
        assert "Bad Request" in str(exc_info.value)

    @patch("cse_lk.client.requests.Session.post")
    def test_make_request_network_error(self, mock_post):
        """Test network error handling."""
        mock_post.side_effect = ConnectionError("Connection failed")

        with pytest.raises(CSENetworkError):
            self.client._make_request("test_endpoint")

    @patch("cse_lk.client.requests.Session.post")
    def test_make_request_timeout(self, mock_post):
        """Test timeout handling."""
        mock_post.side_effect = Timeout("Request timed out")

        with pytest.raises(CSENetworkError):
            self.client._make_request("test_endpoint")

    @patch("cse_lk.client.requests.Session.post")
    def test_make_request_invalid_json(self, mock_post):
        """Test invalid JSON response handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        with pytest.raises(CSEAPIError) as exc_info:
            self.client._make_request("test_endpoint")

        assert "Invalid JSON response" in str(exc_info.value)

    @patch("cse_lk.client.CSEClient._make_request")
    def test_get_company_info(self, mock_request):
        """Test get_company_info method."""
        mock_data = {
            "reqSymbolInfo": {
                "symbol": "LOLC.N0000",
                "name": "L O L C HOLDINGS PLC",
                "lastTradedPrice": 546.5,
                "change": -2.5,
                "changePercentage": -0.455,
                "marketCap": 259696800000,
            },
            "reqLogo": {"id": 2168, "path": "upload_logo/378_1601611239.jpeg"},
            "reqSymbolBetaInfo": {"betaValueSPSL": 1.0227},
        }
        mock_request.return_value = mock_data

        result = self.client.get_company_info("LOLC.N0000")

        assert isinstance(result, CompanyInfo)
        assert result.symbol == "LOLC.N0000"
        assert result.name == "L O L C HOLDINGS PLC"
        assert result.last_traded_price == 546.5
        assert result.beta_value == 1.0227
        assert result.logo is not None
        assert (
            result.logo.full_url
            == "https://cdn.cse.lk/cmt/upload_logo/378_1601611239.jpeg"
        )

        mock_request.assert_called_once_with(
            "companyInfoSummery", {"symbol": "LOLC.N0000"}
        )

    @patch("cse_lk.client.CSEClient._make_request")
    def test_get_market_status(self, mock_request):
        """Test get_market_status method."""
        mock_request.return_value = {"status": "Market Open"}

        result = self.client.get_market_status()

        assert isinstance(result, MarketStatus)
        assert result.status == "Market Open"
        assert result.is_open is True

        mock_request.assert_called_once_with("marketStatus")

    @patch("cse_lk.client.CSEClient._make_request")
    def test_get_aspi_data(self, mock_request):
        """Test get_aspi_data method."""
        mock_request.return_value = {
            "value": 19826.57,
            "change": 21.77,
            "changePercentage": 0.11,
        }

        result = self.client.get_aspi_data()

        assert isinstance(result, IndexData)
        assert result.value == 19826.57
        assert result.change == 21.77
        assert result.change_percentage == 0.11

        mock_request.assert_called_once_with("aspiData")

    @patch("cse_lk.client.CSEClient._make_request")
    def test_get_trade_summary(self, mock_request):
        """Test get_trade_summary method."""
        mock_request.return_value = {
            "reqTradeSummery": [
                {"symbol": "ABAN.N0000", "price": 579.75, "volume": 1000, "trades": 5}
            ]
        }

        result = self.client.get_trade_summary()

        assert len(result) == 1
        assert result[0].symbol == "ABAN.N0000"
        assert result[0].price == 579.75

        mock_request.assert_called_once_with("tradeSummary")

    @patch("cse_lk.client.CSEClient._make_request")
    def test_get_today_share_prices(self, mock_request):
        """Test get_today_share_prices method."""
        mock_request.return_value = [
            {
                "symbol": "ABAN.N0000",
                "lastTradedPrice": 579.75,
                "change": 5.0,
                "changePercentage": 0.87,
            }
        ]

        result = self.client.get_today_share_prices()

        assert len(result) == 1
        assert result[0].symbol == "ABAN.N0000"
        assert result[0].last_traded_price == 579.75

        mock_request.assert_called_once_with("todaySharePrice")

    @patch("cse_lk.client.CSEClient._make_request")
    def test_search_companies(self, mock_request):
        """Test search_companies method."""
        mock_request.return_value = [
            {"symbol": "LOLC.N0000", "lastTradedPrice": 546.5},
            {"symbol": "ABAN.N0000", "lastTradedPrice": 579.75},
            {"symbol": "LOL.X0000", "lastTradedPrice": 100.0},
        ]

        result = self.client.search_companies("LOL")

        assert len(result) == 2  # Should match LOLC.N0000 and LOL.X0000
        symbols = [price.symbol for price in result]
        assert "LOLC.N0000" in symbols
        assert "LOL.X0000" in symbols
        assert "ABAN.N0000" not in symbols

    def test_search_companies_empty_query(self):
        """Test search_companies with empty query."""
        with pytest.raises(CSEValidationError):
            self.client.search_companies("")

    @patch("cse_lk.client.CSEClient.get_market_status")
    @patch("cse_lk.client.CSEClient.get_market_summary")
    @patch("cse_lk.client.CSEClient.get_aspi_data")
    @patch("cse_lk.client.CSEClient.get_snp_data")
    @patch("cse_lk.client.CSEClient.get_top_gainers")
    @patch("cse_lk.client.CSEClient.get_top_losers")
    @patch("cse_lk.client.CSEClient.get_most_active_trades")
    def test_get_market_overview(
        self,
        mock_active,
        mock_losers,
        mock_gainers,
        mock_snp,
        mock_aspi,
        mock_summary,
        mock_status,
    ):
        """Test get_market_overview method."""
        # Mock return values
        mock_status.return_value = MarketStatus(status="Market Open")
        mock_gainers.return_value = [Mock() for _ in range(10)]  # 10 gainers
        mock_losers.return_value = [Mock() for _ in range(10)]  # 10 losers
        mock_active.return_value = [Mock() for _ in range(10)]  # 10 active

        result = self.client.get_market_overview()

        assert "status" in result
        assert "summary" in result
        assert "aspi" in result
        assert "snp_sl20" in result
        assert "top_gainers" in result
        assert "top_losers" in result
        assert "most_active" in result

        # Should limit to top 5
        assert len(result["top_gainers"]) == 5
        assert len(result["top_losers"]) == 5
        assert len(result["most_active"]) == 5

    def test_context_manager(self):
        """Test client as context manager."""
        with patch("cse_lk.client.requests.Session.close") as mock_close:
            with CSEClient() as client:
                assert isinstance(client, CSEClient)
            mock_close.assert_called_once()


class TestDataModels:
    """Test cases for data models."""

    def test_company_info_from_dict(self):
        """Test CompanyInfo.from_dict method."""
        data = {
            "reqSymbolInfo": {
                "symbol": "TEST.N0000",
                "name": "Test Company",
                "lastTradedPrice": 100.0,
                "change": 5.0,
                "changePercentage": 5.0,
                "marketCap": 1000000000,
            },
            "reqLogo": {"id": 123, "path": "test_logo.jpg"},
            "reqSymbolBetaInfo": {"betaValueSPSL": 1.5},
        }

        company_info = CompanyInfo.from_dict(data)

        assert company_info.symbol == "TEST.N0000"
        assert company_info.name == "Test Company"
        assert company_info.last_traded_price == 100.0
        assert company_info.change == 5.0
        assert company_info.change_percentage == 5.0
        assert company_info.market_cap == 1000000000
        assert company_info.beta_value == 1.5
        assert company_info.logo.id == 123
        assert company_info.logo.path == "test_logo.jpg"
        assert company_info.logo.full_url == "https://cdn.cse.lk/cmt/test_logo.jpg"

    def test_market_status_is_open(self):
        """Test MarketStatus.is_open property."""
        open_status = MarketStatus(status="Market Open")
        closed_status = MarketStatus(status="Market Closed")

        assert open_status.is_open is True
        assert closed_status.is_open is False


if __name__ == "__main__":
    pytest.main([__file__])
