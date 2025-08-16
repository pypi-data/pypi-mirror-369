"""Data models for CSE API responses."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class CompanyLogo:
    """Company logo information."""

    id: Optional[int]
    path: str

    @property
    def full_url(self) -> str:
        """Get the full URL for the company logo."""
        return f"https://cdn.cse.lk/cmt/{self.path}"


@dataclass
class CompanyInfo:
    """Detailed company information."""

    symbol: str
    name: str
    last_traded_price: float
    change: float
    change_percentage: float
    market_cap: Optional[float] = None
    beta_value: Optional[float] = None
    logo: Optional[CompanyLogo] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompanyInfo":
        """Create CompanyInfo from API response dictionary."""
        symbol_info = data.get("reqSymbolInfo", {})
        logo_info = data.get("reqLogo", {})
        beta_info = data.get("reqSymbolBetaInfo", {})

        logo = None
        if logo_info and logo_info.get("path"):
            logo = CompanyLogo(id=logo_info.get("id"), path=logo_info["path"])

        return cls(
            symbol=symbol_info.get("symbol", ""),
            name=symbol_info.get("name", ""),
            last_traded_price=float(symbol_info.get("lastTradedPrice", 0)),
            change=float(symbol_info.get("change", 0)),
            change_percentage=float(symbol_info.get("changePercentage", 0)),
            market_cap=symbol_info.get("marketCap"),
            beta_value=beta_info.get("betaValueSPSL"),
            logo=logo,
        )


@dataclass
class TradeSummary:
    """Trade summary for a security."""

    symbol: str
    price: float
    volume: Optional[int] = None
    trades: Optional[int] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeSummary":
        """Create TradeSummary from API response dictionary."""
        return cls(
            symbol=data.get("symbol", ""),
            price=float(data.get("price", 0)),
            volume=data.get("volume"),
            trades=data.get("trades"),
            change=data.get("change"),
            change_percentage=data.get("changePercentage"),
        )


@dataclass
class SharePrice:
    """Today's share price data."""

    symbol: str
    last_traded_price: float
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharePrice":
        """Create SharePrice from API response dictionary."""
        return cls(
            symbol=data.get("symbol", ""),
            last_traded_price=float(data.get("lastTradedPrice", 0)),
            change=data.get("change"),
            change_percentage=data.get("changePercentage"),
            high=data.get("high"),
            low=data.get("low"),
            volume=data.get("volume"),
        )


@dataclass
class TopGainer:
    """Top gaining stock information."""

    symbol: str
    change_percentage: float
    price: Optional[float] = None
    change: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopGainer":
        """Create TopGainer from API response dictionary."""
        return cls(
            symbol=data.get("symbol", ""),
            change_percentage=float(data.get("changePercentage", 0)),
            price=data.get("price"),
            change=data.get("change"),
        )


@dataclass
class TopLoser:
    """Top losing stock information."""

    symbol: str
    change_percentage: float
    price: Optional[float] = None
    change: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopLoser":
        """Create TopLoser from API response dictionary."""
        return cls(
            symbol=data.get("symbol", ""),
            change_percentage=float(data.get("changePercentage", 0)),
            price=data.get("price"),
            change=data.get("change"),
        )


@dataclass
class ActiveTrade:
    """Most active trade information."""

    symbol: str
    trade_volume: float
    price: Optional[float] = None
    volume: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActiveTrade":
        """Create ActiveTrade from API response dictionary."""
        return cls(
            symbol=data.get("symbol", ""),
            trade_volume=float(data.get("tradeVolume", 0)),
            price=data.get("price"),
            volume=data.get("volume"),
        )


@dataclass
class MarketStatus:
    """Market status information."""

    status: str

    @property
    def is_open(self) -> bool:
        """Check if market is currently open."""
        return "open" in self.status.lower()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketStatus":
        """Create MarketStatus from API response dictionary."""
        return cls(status=data.get("status", "Unknown"))


@dataclass
class MarketSummary:
    """Market summary data."""

    trade_volume: float
    share_volume: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketSummary":
        """Create MarketSummary from API response dictionary."""
        return cls(
            trade_volume=float(data.get("tradeVolume", 0)),
            share_volume=int(data.get("shareVolume", 0)),
        )


@dataclass
class IndexData:
    """Stock index data (ASPI, S&P SL20, etc.)."""

    value: float
    change: float
    change_percentage: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndexData":
        """Create IndexData from API response dictionary."""
        return cls(
            value=float(data.get("value", 0)),
            change=float(data.get("change", 0)),
            change_percentage=data.get("changePercentage"),
        )


@dataclass
class Sector:
    """Sector information."""

    symbol: str
    index_name: str
    value: Optional[float] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sector":
        """Create Sector from API response dictionary."""
        return cls(
            symbol=data.get("symbol", ""),
            index_name=data.get("indexName", ""),
            value=data.get("value"),
            change=data.get("change"),
            change_percentage=data.get("changePercentage"),
        )


@dataclass
class DetailedTrade:
    """Detailed trade information."""

    id: int
    name: str
    symbol: str
    price: float
    quantity: int
    trades: int
    change: float
    change_percentage: float
    security_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetailedTrade":
        """Create DetailedTrade from API response dictionary."""
        return cls(
            id=int(data.get("id", 0)),
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            price=float(data.get("price", 0)),
            quantity=int(data.get("qty", 0)),
            trades=int(data.get("trades", 0)),
            change=float(data.get("change", 0)),
            change_percentage=float(data.get("changePercentage", 0)),
            security_id=data.get("securityId"),
        )


@dataclass
class DailyMarketSummary:
    """Daily market summary data."""

    id: int
    trade_date: datetime
    market_turnover: float
    market_trades: float
    market_domestic: float
    market_foreign: float
    equity_turnover: float
    equity_domestic_purchase: float
    equity_domestic_sales: float
    equity_foreign_purchase: float
    equity_foreign_sales: float
    volume_of_turnover_number: float
    volume_of_turnover_domestic: float
    volume_of_turnover_foreign: float
    trades_no: int
    trades_no_domestic: int
    trades_no_foreign: int
    listed_company_number: int
    trade_company_number: int
    market_cap: float
    asi: float
    spp: float
    per: Optional[float] = None
    pbv: Optional[float] = None
    dy: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyMarketSummary":
        """Create DailyMarketSummary from API response dictionary."""
        # Convert timestamp to datetime
        trade_date = datetime.fromtimestamp(data.get("tradeDate", 0) / 1000)

        return cls(
            id=int(data.get("id", 0)),
            trade_date=trade_date,
            market_turnover=float(data.get("marketTurnover", 0)),
            market_trades=float(data.get("marketTrades", 0)),
            market_domestic=float(data.get("marketDomestic", 0)),
            market_foreign=float(data.get("marketForeign", 0)),
            equity_turnover=float(data.get("equityTurnover", 0)),
            equity_domestic_purchase=float(data.get("equityDomesticPurchase", 0)),
            equity_domestic_sales=float(data.get("equityDomesticSales", 0)),
            equity_foreign_purchase=float(data.get("equityForeignPurchase", 0)),
            equity_foreign_sales=float(data.get("equityForeignSales", 0)),
            volume_of_turnover_number=float(data.get("volumeOfTurnOverNumber", 0)),
            volume_of_turnover_domestic=float(data.get("volumeOfTurnoverDomestic", 0)),
            volume_of_turnover_foreign=float(data.get("volumeOfTurnoverForeign", 0)),
            trades_no=int(data.get("tradesNo", 0)),
            trades_no_domestic=int(data.get("tradesNoDomestic", 0)),
            trades_no_foreign=int(data.get("tradesNoForeign", 0)),
            listed_company_number=int(data.get("listedCompanyNumber", 0)),
            trade_company_number=int(data.get("tradeCompanyNumber", 0)),
            market_cap=float(data.get("marketCap", 0)),
            asi=float(data.get("asi", 0)),
            spp=float(data.get("spp", 0)),
            per=data.get("per"),
            pbv=data.get("pbv"),
            dy=data.get("dy"),
        )


@dataclass
class Announcement:
    """Announcement information."""

    company: str
    file_text: Optional[str] = None
    symbol: Optional[str] = None
    date: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Announcement":
        """Create Announcement from API response dictionary."""
        return cls(
            company=data.get("company", ""),
            file_text=data.get("fileText"),
            symbol=data.get("symbol"),
            date=data.get("date"),
        )
