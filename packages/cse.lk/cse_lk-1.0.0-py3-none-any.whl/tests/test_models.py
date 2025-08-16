"""Unit tests for data models."""

import pytest
from datetime import datetime
from cse_lk.models import (
    CompanyInfo,
    CompanyLogo,
    TradeSummary,
    MarketStatus,
    DetailedTrade,
    DailyMarketSummary,
    Announcement,
)


class TestCompanyLogo:
    """Test cases for CompanyLogo model."""

    def test_full_url_property(self):
        """Test the full_url property."""
        logo = CompanyLogo(id=123, path="upload_logo/test.jpg")
        expected_url = "https://cdn.cse.lk/cmt/upload_logo/test.jpg"
        assert logo.full_url == expected_url


class TestCompanyInfo:
    """Test cases for CompanyInfo model."""

    def test_from_dict_complete(self):
        """Test creating CompanyInfo from complete dictionary."""
        data = {
            "reqSymbolInfo": {
                "symbol": "TEST.N0000",
                "name": "Test Company Ltd",
                "lastTradedPrice": 150.5,
                "change": 10.5,
                "changePercentage": 7.5,
                "marketCap": 2000000000,
            },
            "reqLogo": {"id": 456, "path": "upload_logo/test_company.png"},
            "reqSymbolBetaInfo": {"betaValueSPSL": 1.25},
        }

        company = CompanyInfo.from_dict(data)

        assert company.symbol == "TEST.N0000"
        assert company.name == "Test Company Ltd"
        assert company.last_traded_price == 150.5
        assert company.change == 10.5
        assert company.change_percentage == 7.5
        assert company.market_cap == 2000000000
        assert company.beta_value == 1.25
        assert company.logo.id == 456
        assert company.logo.path == "upload_logo/test_company.png"

    def test_from_dict_minimal(self):
        """Test creating CompanyInfo from minimal dictionary."""
        data = {
            "reqSymbolInfo": {
                "symbol": "MINIMAL.N0000",
                "name": "Minimal Company",
                "lastTradedPrice": 50.0,
                "change": 0.0,
                "changePercentage": 0.0,
            }
        }

        company = CompanyInfo.from_dict(data)

        assert company.symbol == "MINIMAL.N0000"
        assert company.name == "Minimal Company"
        assert company.last_traded_price == 50.0
        assert company.change == 0.0
        assert company.change_percentage == 0.0
        assert company.market_cap is None
        assert company.beta_value is None
        assert company.logo is None

    def test_from_dict_empty(self):
        """Test creating CompanyInfo from empty dictionary."""
        data = {}

        company = CompanyInfo.from_dict(data)

        assert company.symbol == ""
        assert company.name == ""
        assert company.last_traded_price == 0.0
        assert company.change == 0.0
        assert company.change_percentage == 0.0
        assert company.market_cap is None
        assert company.beta_value is None
        assert company.logo is None


class TestTradeSummary:
    """Test cases for TradeSummary model."""

    def test_from_dict_complete(self):
        """Test creating TradeSummary from complete dictionary."""
        data = {
            "symbol": "TRADE.N0000",
            "price": 125.75,
            "volume": 5000,
            "trades": 25,
            "change": 3.25,
            "changePercentage": 2.66,
        }

        trade = TradeSummary.from_dict(data)

        assert trade.symbol == "TRADE.N0000"
        assert trade.price == 125.75
        assert trade.volume == 5000
        assert trade.trades == 25
        assert trade.change == 3.25
        assert trade.change_percentage == 2.66

    def test_from_dict_minimal(self):
        """Test creating TradeSummary from minimal dictionary."""
        data = {"symbol": "MIN.N0000", "price": 100.0}

        trade = TradeSummary.from_dict(data)

        assert trade.symbol == "MIN.N0000"
        assert trade.price == 100.0
        assert trade.volume is None
        assert trade.trades is None
        assert trade.change is None
        assert trade.change_percentage is None


class TestMarketStatus:
    """Test cases for MarketStatus model."""

    def test_is_open_true(self):
        """Test is_open property when market is open."""
        status = MarketStatus(status="Market Open")
        assert status.is_open is True

        status = MarketStatus(status="Pre-Market Open")
        assert status.is_open is True

        status = MarketStatus(status="OPEN")
        assert status.is_open is True

    def test_is_open_false(self):
        """Test is_open property when market is closed."""
        status = MarketStatus(status="Market Closed")
        assert status.is_open is False

        status = MarketStatus(status="CLOSED")
        assert status.is_open is False

        status = MarketStatus(status="Suspended")
        assert status.is_open is False

    def test_from_dict(self):
        """Test creating MarketStatus from dictionary."""
        data = {"status": "Market Open"}
        status = MarketStatus.from_dict(data)
        assert status.status == "Market Open"

        # Test with empty data
        data = {}
        status = MarketStatus.from_dict(data)
        assert status.status == "Unknown"


class TestDailyMarketSummary:
    """Test cases for DailyMarketSummary model."""

    def test_from_dict_complete(self):
        """Test creating DailyMarketSummary from complete dictionary."""
        timestamp = 1703980800000  # 2023-12-31 00:00:00 UTC in milliseconds
        data = {
            "id": 12345,
            "tradeDate": timestamp,
            "marketTurnover": 3.26376192e9,
            "marketTrades": 30274.0,
            "marketDomestic": 30003.0,
            "marketForeign": 271.0,
            "equityTurnover": 3.26376192e9,
            "equityDomesticPurchase": 3.15549645e9,
            "equityDomesticSales": 3.18251674e9,
            "equityForeignPurchase": 1.08265512e8,
            "equityForeignSales": 8.1245208e7,
            "volumeOfTurnOverNumber": 1.15084304e8,
            "volumeOfTurnoverDomestic": 1.13407144e8,
            "volumeOfTurnoverForeign": 1677157,
            "tradesNo": 30274,
            "tradesNoDomestic": 30003,
            "tradesNoForeign": 271,
            "listedCompanyNumber": 286,
            "tradeCompanyNumber": 264,
            "marketCap": 6.940225783432e12,
            "asi": 19826.57,
            "spp": 5825.39,
            "per": 9.2,
            "pbv": 1.3,
            "dy": 2.5,
        }

        summary = DailyMarketSummary.from_dict(data)

        assert summary.id == 12345
        assert summary.trade_date == datetime.fromtimestamp(timestamp / 1000)
        assert summary.market_turnover == 3.26376192e9
        assert summary.market_trades == 30274.0
        assert summary.market_domestic == 30003.0
        assert summary.market_foreign == 271.0
        assert summary.equity_turnover == 3.26376192e9
        assert summary.trades_no == 30274
        assert summary.trades_no_domestic == 30003
        assert summary.trades_no_foreign == 271
        assert summary.listed_company_number == 286
        assert summary.trade_company_number == 264
        assert summary.market_cap == 6.940225783432e12
        assert summary.asi == 19826.57
        assert summary.spp == 5825.39
        assert summary.per == 9.2
        assert summary.pbv == 1.3
        assert summary.dy == 2.5

    def test_from_dict_minimal(self):
        """Test creating DailyMarketSummary from minimal dictionary."""
        data = {
            "id": 1,
            "tradeDate": 0,
            "marketTurnover": 0.0,
            "marketTrades": 0.0,
            "marketDomestic": 0.0,
            "marketForeign": 0.0,
            "equityTurnover": 0.0,
            "equityDomesticPurchase": 0.0,
            "equityDomesticSales": 0.0,
            "equityForeignPurchase": 0.0,
            "equityForeignSales": 0.0,
            "volumeOfTurnOverNumber": 0.0,
            "volumeOfTurnoverDomestic": 0.0,
            "volumeOfTurnoverForeign": 0.0,
            "tradesNo": 0,
            "tradesNoDomestic": 0,
            "tradesNoForeign": 0,
            "listedCompanyNumber": 0,
            "tradeCompanyNumber": 0,
            "marketCap": 0.0,
            "asi": 0.0,
            "spp": 0.0,
        }

        summary = DailyMarketSummary.from_dict(data)

        assert summary.id == 1
        assert summary.trade_date == datetime.fromtimestamp(0)
        assert summary.per is None
        assert summary.pbv is None
        assert summary.dy is None


class TestDetailedTrade:
    """Test cases for DetailedTrade model."""

    def test_from_dict_complete(self):
        """Test creating DetailedTrade from complete dictionary."""
        data = {
            "id": 204,
            "securityId": 1001,
            "name": "ABANS ELECTRICALS PLC",
            "symbol": "ABAN.N0000",
            "price": 585.0,
            "qty": 562,
            "trades": 7,
            "change": 29.0,
            "changePercentage": 5.215827338129497,
        }

        trade = DetailedTrade.from_dict(data)

        assert trade.id == 204
        assert trade.security_id == 1001
        assert trade.name == "ABANS ELECTRICALS PLC"
        assert trade.symbol == "ABAN.N0000"
        assert trade.price == 585.0
        assert trade.quantity == 562
        assert trade.trades == 7
        assert trade.change == 29.0
        assert trade.change_percentage == 5.215827338129497

    def test_from_dict_minimal(self):
        """Test creating DetailedTrade from minimal dictionary."""
        data = {}

        trade = DetailedTrade.from_dict(data)

        assert trade.id == 0
        assert trade.security_id is None
        assert trade.name == ""
        assert trade.symbol == ""
        assert trade.price == 0.0
        assert trade.quantity == 0
        assert trade.trades == 0
        assert trade.change == 0.0
        assert trade.change_percentage == 0.0


class TestAnnouncement:
    """Test cases for Announcement model."""

    def test_from_dict_complete(self):
        """Test creating Announcement from complete dictionary."""
        data = {
            "company": "LANKEM DEVELOPMENTS PLC",
            "fileText": "Annual Report 2024",
            "symbol": "LDEV",
            "date": "2024-01-15",
        }

        announcement = Announcement.from_dict(data)

        assert announcement.company == "LANKEM DEVELOPMENTS PLC"
        assert announcement.file_text == "Annual Report 2024"
        assert announcement.symbol == "LDEV"
        assert announcement.date == "2024-01-15"

    def test_from_dict_minimal(self):
        """Test creating Announcement from minimal dictionary."""
        data = {"company": "Test Company"}

        announcement = Announcement.from_dict(data)

        assert announcement.company == "Test Company"
        assert announcement.file_text is None
        assert announcement.symbol is None
        assert announcement.date is None

    def test_from_dict_empty(self):
        """Test creating Announcement from empty dictionary."""
        data = {}

        announcement = Announcement.from_dict(data)

        assert announcement.company == ""
        assert announcement.file_text is None
        assert announcement.symbol is None
        assert announcement.date is None


if __name__ == "__main__":
    pytest.main([__file__])
