# API Reference - CSE.LK

Complete API reference for the CSE.LK Python client.

## CSEClient

The main client class for accessing the CSE API.

### Constructor

```python
CSEClient(
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_delay: Optional[float] = None,
    session: Optional[requests.Session] = None
)
```

**Parameters:**
- `timeout` (int, optional): Request timeout in seconds. Default: 30
- `max_retries` (int, optional): Maximum retry attempts. Default: 3
- `retry_delay` (float, optional): Delay between retries in seconds. Default: 1
- `session` (requests.Session, optional): Custom requests session

### Market Data Methods

#### get_company_info(symbol: str) → CompanyInfo

Get detailed information for a specific company.

```python
company = client.get_company_info("LOLC.N0000")
print(company.name)  # "L O L C HOLDINGS PLC"
```

#### get_trade_summary() → List[TradeSummary]

Get trade summary for all securities.

```python
trades = client.get_trade_summary()
for trade in trades:
    print(f"{trade.symbol}: {trade.price}")
```

#### get_today_share_prices() → List[SharePrice]

Get today's share price data for all securities.

```python
prices = client.get_today_share_prices()
for price in prices:
    print(f"{price.symbol}: LKR {price.last_traded_price}")
```

#### get_top_gainers() → List[TopGainer]

Get list of top gaining stocks.

```python
gainers = client.get_top_gainers()
for gainer in gainers[:5]:
    print(f"{gainer.symbol}: +{gainer.change_percentage:.2f}%")
```

#### get_top_losers() → List[TopLoser]

Get list of top losing stocks.

```python
losers = client.get_top_losers()
for loser in losers[:5]:
    print(f"{loser.symbol}: {loser.change_percentage:.2f}%")
```

#### get_most_active_trades() → List[ActiveTrade]

Get most active trades by volume.

```python
active = client.get_most_active_trades()
for trade in active[:5]:
    print(f"{trade.symbol}: Volume {trade.trade_volume:,.0f}")
```

#### get_market_status() → MarketStatus

Get current market status (open/closed).

```python
status = client.get_market_status()
print(f"Market is {'open' if status.is_open else 'closed'}")
```

#### get_market_summary() → MarketSummary

Get market summary data.

```python
summary = client.get_market_summary()
print(f"Trade Volume: {summary.trade_volume}")
```

#### get_aspi_data() → IndexData

Get All Share Price Index (ASPI) data.

```python
aspi = client.get_aspi_data()
print(f"ASPI: {aspi.value:.2f} ({aspi.change:+.2f})")
```

#### get_snp_data() → IndexData

Get S&P Sri Lanka 20 Index data.

```python
snp = client.get_snp_data()
print(f"S&P SL20: {snp.value:.2f} ({snp.change:+.2f})")
```

#### get_chart_data(symbol: str) → Dict[str, Any]

Get chart data for a specific stock.

**Note:** This endpoint may return HTTP 400 for some symbols.

```python
chart_data = client.get_chart_data("LOLC.N0000")
```

#### get_all_sectors() → List[Sector]

Get data for all sectors.

```python
sectors = client.get_all_sectors()
for sector in sectors:
    print(f"{sector.symbol}: {sector.index_name}")
```

#### get_detailed_trades(symbol: Optional[str] = None) → List[DetailedTrade]

Get detailed trade information.

```python
# All detailed trades
all_trades = client.get_detailed_trades()

# Trades for specific symbol
symbol_trades = client.get_detailed_trades("LOLC.N0000")
```

#### get_daily_market_summary() → List[DailyMarketSummary]

Get daily market summary data.

```python
daily_summary = client.get_daily_market_summary()
for day in daily_summary[:5]:
    print(f"{day.trade_date}: LKR {day.market_turnover:,.0f}")
```

### Announcement Methods

#### get_new_listings_announcements() → List[Announcement]

Get new listings and related announcements.

#### get_buy_in_board_announcements() → List[Announcement]

Get buy-in board announcements.

#### get_approved_announcements() → List[Announcement]

Get approved announcements.

#### get_covid_announcements() → List[Announcement]

Get COVID-related announcements.

#### get_financial_announcements() → List[Announcement]

Get financial announcements.

#### get_circular_announcements() → List[Announcement]

Get circular announcements.

#### get_directive_announcements() → List[Announcement]

Get directive announcements.

#### get_non_compliance_announcements() → List[Announcement]

Get non-compliance announcements.

### Convenience Methods

#### search_companies(query: str) → List[SharePrice]

Search for companies by name or symbol.

```python
results = client.search_companies("BANK")
for result in results:
    print(f"{result.symbol}: LKR {result.last_traded_price}")
```

#### get_market_overview() → Dict[str, Any]

Get a comprehensive market overview.

```python
overview = client.get_market_overview()
# Returns:
# {
#     "status": MarketStatus,
#     "summary": MarketSummary,
#     "aspi": IndexData,
#     "snp_sl20": IndexData,
#     "top_gainers": List[TopGainer],  # Top 5
#     "top_losers": List[TopLoser],    # Top 5
#     "most_active": List[ActiveTrade] # Top 5
# }
```

## Data Models

### CompanyInfo

```python
@dataclass
class CompanyInfo:
    symbol: str
    name: str
    last_traded_price: float
    change: float
    change_percentage: float
    market_cap: Optional[float] = None
    beta_value: Optional[float] = None
    logo: Optional[CompanyLogo] = None
```

### CompanyLogo

```python
@dataclass
class CompanyLogo:
    id: Optional[int]
    path: str
    
    @property
    def full_url(self) -> str:
        """Get the full URL for the company logo."""
        return f"https://cdn.cse.lk/cmt/{self.path}"
```

### SharePrice

```python
@dataclass
class SharePrice:
    symbol: str
    last_traded_price: float
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
```

### MarketStatus

```python
@dataclass
class MarketStatus:
    status: str
    
    @property
    def is_open(self) -> bool:
        """Check if market is currently open."""
        return "open" in self.status.lower()
```

### IndexData

```python
@dataclass
class IndexData:
    value: float
    change: float
    change_percentage: Optional[float] = None
```

### DetailedTrade

```python
@dataclass
class DetailedTrade:
    id: int
    name: str
    symbol: str
    price: float
    quantity: int
    trades: int
    change: float
    change_percentage: float
    security_id: Optional[int] = None
```

### DailyMarketSummary

```python
@dataclass
class DailyMarketSummary:
    id: int
    trade_date: datetime
    market_turnover: float
    market_trades: float
    market_domestic: float
    market_foreign: float
    equity_turnover: float
    # ... many more fields
    asi: float
    spp: float
    per: Optional[float] = None
    pbv: Optional[float] = None
    dy: Optional[float] = None
```

### Announcement

```python
@dataclass
class Announcement:
    company: str
    file_text: Optional[str] = None
    symbol: Optional[str] = None
    date: Optional[str] = None
```

## Exceptions

### CSEError

Base exception for all CSE API related errors.

```python
class CSEError(Exception):
    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.response_data = response_data or {}
```

### CSEAPIError

Raised when the CSE API returns an error response.

```python
class CSEAPIError(CSEError):
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
```

### CSENetworkError

Raised when there's a network-related error.

### CSEValidationError

Raised when input validation fails.

### CSEAuthenticationError

Raised when authentication fails.

### CSERateLimitError

Raised when API rate limits are exceeded.

```python
class CSERateLimitError(CSEError):
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.retry_after = retry_after
```

## Context Manager Support

The client supports context manager usage for automatic session cleanup:

```python
with CSEClient() as client:
    # Use client here
    company = client.get_company_info("LOLC.N0000")
# Session is automatically closed
```

## Type Hints

All methods are fully type-hinted for better IDE support and code safety. Import types:

```python
from cse_lk import CSEClient
from cse_lk.models import CompanyInfo, MarketStatus, IndexData
from cse_lk.exceptions import CSEError, CSEValidationError
``` 