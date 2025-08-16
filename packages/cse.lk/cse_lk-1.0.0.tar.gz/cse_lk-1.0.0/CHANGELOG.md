# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of CSE.LK Python client
- Complete API coverage for all 22 CSE endpoints
- Type-safe data models for all API responses
- Comprehensive error handling with custom exception hierarchy
- Built-in retry logic with exponential backoff
- Rate limiting support
- Context manager support for automatic session cleanup
- Extensive documentation and examples
- Comprehensive test suite with >95% coverage
- Support for Python 3.7+

### Features
- **Market Data Methods:**
  - `get_company_info()` - Get detailed company information
  - `get_trade_summary()` - Get trade summary for all securities
  - `get_today_share_prices()` - Get today's share prices
  - `get_top_gainers()` - Get top gaining stocks
  - `get_top_losers()` - Get top losing stocks
  - `get_most_active_trades()` - Get most active trades
  - `get_market_status()` - Get market open/close status
  - `get_market_summary()` - Get market summary data
  - `get_aspi_data()` - Get All Share Price Index data
  - `get_snp_data()` - Get S&P Sri Lanka 20 Index data
  - `get_all_sectors()` - Get all sector data
  - `get_detailed_trades()` - Get detailed trade information
  - `get_daily_market_summary()` - Get daily market summary

- **Announcement Methods:**
  - `get_new_listings_announcements()` - New listings announcements
  - `get_buy_in_board_announcements()` - Buy-in board announcements
  - `get_approved_announcements()` - Approved announcements
  - `get_covid_announcements()` - COVID-related announcements
  - `get_financial_announcements()` - Financial announcements
  - `get_circular_announcements()` - Circular announcements
  - `get_directive_announcements()` - Directive announcements
  - `get_non_compliance_announcements()` - Non-compliance announcements

- **Convenience Methods:**
  - `search_companies()` - Search companies by symbol or name
  - `get_market_overview()` - Get comprehensive market overview

- **Data Models:**
  - `CompanyInfo` - Company details with logo and financial data
  - `TradeSummary` - Trade summary with volume and price data
  - `SharePrice` - Current share price with change information
  - `MarketStatus` - Market status with convenience methods
  - `IndexData` - Index values with change data
  - `DetailedTrade` - Detailed trade information
  - `DailyMarketSummary` - Comprehensive daily market statistics
  - `Announcement` - Company announcements and notices

- **Exception Handling:**
  - `CSEError` - Base exception class
  - `CSEAPIError` - API response errors
  - `CSENetworkError` - Network/connection errors
  - `CSEValidationError` - Input validation errors
  - `CSEAuthenticationError` - Authentication failures
  - `CSERateLimitError` - Rate limiting errors

### Documentation
- Comprehensive README with usage examples
- Quick start guide
- Complete API reference
- Advanced usage examples
- Market analysis examples
- Full type hints for IDE support

### Testing
- Unit tests for all client methods
- Data model tests
- Exception handling tests
- Mock API responses for reliable testing
- Coverage reports

### Build and Distribution
- Modern Python packaging with `pyproject.toml`
- Support for both source and wheel distributions
- Automated build and upload scripts
- PyPI and Test PyPI support
- Development environment setup

## [Unreleased]

### Planned Features
- Caching mechanism for frequently accessed data
- Async/await support for concurrent requests
- WebSocket support for real-time data
- Data visualization helpers
- Performance optimizations
- Additional convenience methods

---

For a complete list of changes, see the [commit history](https://github.com/your-username/cse.lk/commits/main).

For upgrade instructions, see the [migration guide](docs/MIGRATION.md). 