# Quick Start Guide - CSE.LK

This guide will get you up and running with the CSE.LK Python client in minutes.

## Installation

```bash
pip install cse.lk
```

## Basic Usage

### 1. Initialize the Client

```python
from cse_lk import CSEClient

# Create a client instance
client = CSEClient()

# Or with custom configuration
client = CSEClient(
    timeout=60,        # Request timeout in seconds
    max_retries=5,     # Maximum retry attempts
    retry_delay=2.0    # Delay between retries
)
```

### 2. Get Company Information

```python
# Get detailed company information
company = client.get_company_info("LOLC.N0000")

print(f"Company: {company.name}")
print(f"Symbol: {company.symbol}")
print(f"Price: LKR {company.last_traded_price}")
print(f"Change: {company.change:+.2f} ({company.change_percentage:+.2f}%)")

# Access company logo
if company.logo:
    print(f"Logo URL: {company.logo.full_url}")
```

### 3. Market Overview

```python
# Get comprehensive market overview
overview = client.get_market_overview()

print(f"Market Status: {overview['status'].status}")
print(f"ASPI: {overview['aspi'].value:.2f}")
print(f"S&P SL20: {overview['snp_sl20'].value:.2f}")

# Top performers
print("\nTop Gainers:")
for gainer in overview['top_gainers']:
    print(f"  {gainer.symbol}: +{gainer.change_percentage:.2f}%")
```

### 4. Search Companies

```python
# Search for companies by symbol
results = client.search_companies("BANK")

print(f"Found {len(results)} companies:")
for company in results:
    print(f"  {company.symbol}: LKR {company.last_traded_price}")
```

### 5. Market Data

```python
# Get today's share prices
prices = client.get_today_share_prices()
print(f"Total stocks: {len(prices)}")

# Get top gainers and losers
gainers = client.get_top_gainers()
losers = client.get_top_losers()

print(f"Top gainer: {gainers[0].symbol} (+{gainers[0].change_percentage:.2f}%)")
print(f"Top loser: {losers[0].symbol} ({losers[0].change_percentage:.2f}%)")

# Get most active trades
active = client.get_most_active_trades()
print(f"Most active: {active[0].symbol} (Volume: {active[0].trade_volume:,.0f})")
```

### 6. Market Indices

```python
# Get ASPI data
aspi = client.get_aspi_data()
print(f"ASPI: {aspi.value:.2f} ({aspi.change:+.2f})")

# Get S&P Sri Lanka 20 data
snp = client.get_snp_data()
print(f"S&P SL20: {snp.value:.2f} ({snp.change:+.2f})")
```

### 7. Announcements

```python
# Get various types of announcements
financial = client.get_financial_announcements()
approved = client.get_approved_announcements()
circular = client.get_circular_announcements()

print(f"Financial announcements: {len(financial)}")
print(f"Approved announcements: {len(approved)}")
print(f"Circular announcements: {len(circular)}")

# Display recent financial announcements
for announcement in financial[:3]:
    print(f"  {announcement.company}: {announcement.file_text}")
```

## Error Handling

```python
from cse_lk import CSEClient, CSEError, CSEValidationError, CSENetworkError

client = CSEClient()

try:
    company = client.get_company_info("INVALID_SYMBOL")
except CSEValidationError as e:
    print(f"Validation error: {e}")
except CSENetworkError as e:
    print(f"Network error: {e}")
except CSEError as e:
    print(f"General CSE error: {e}")
```

## Context Manager

```python
# Use context manager for automatic session cleanup
with CSEClient() as client:
    company = client.get_company_info("LOLC.N0000")
    market_status = client.get_market_status()
    # Session will be automatically closed
```

## Next Steps

- Check out the [examples](../examples/) directory for more advanced usage
- Read the full [API documentation](API_REFERENCE.md)
- See [ADVANCED_USAGE.md](ADVANCED_USAGE.md) for performance tips and best practices

## Common Stock Symbols

Here are some popular CSE stock symbols to get you started:

- `LOLC.N0000` - LOLC Holdings PLC
- `COMB.N0000` - Commercial Bank of Ceylon PLC
- `SAMP.N0000` - Sampath Bank PLC
- `HNB.N0000` - Hatton National Bank PLC
- `NDB.N0000` - National Development Bank PLC
- `JKH.N0000` - John Keells Holdings PLC
- `DIAL.N0000` - Dialog Axiata PLC
- `EXPO.N0000` - Expolanka Holdings PLC

## Support

If you encounter any issues or have questions:

1. Check the [documentation](../README.md)
2. Look at the [examples](../examples/)
3. Open an issue on GitHub
4. Read the [FAQ](FAQ.md)

Happy trading! 📈🚀 