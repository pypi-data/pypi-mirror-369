#!/usr/bin/env python3
"""
Basic usage examples for the CSE.LK Python client.

This script demonstrates how to use the most common features of the CSE API client.
"""

from cse_lk import CSEClient
from cse_lk.exceptions import CSEError


def main():
    """Main example function."""
    print("🏢 CSE.LK Python Client - Basic Usage Examples")
    print("=" * 50)

    # Initialize the client
    client = CSEClient()

    try:
        # Example 1: Get company information
        print("\n📊 Example 1: Company Information")
        print("-" * 30)
        company = client.get_company_info("LOLC.N0000")
        print(f"Company: {company.name}")
        print(f"Symbol: {company.symbol}")
        print(f"Last Price: LKR {company.last_traded_price}")
        print(f"Change: {company.change:+.2f} " f"({company.change_percentage:+.2f}%)")
        if company.logo:
            print(f"Logo: {company.logo.full_url}")

        # Example 2: Market status and overview
        print("\n📈 Example 2: Market Overview")
        print("-" * 30)
        overview = client.get_market_overview()
        print(f"Market Status: {overview['status'].status}")
        print(f"ASPI: {overview['aspi'].value:.2f} ({overview['aspi'].change:+.2f})")
        print(
            f"S&P SL20: {overview['snp_sl20'].value:.2f} "
            f"({overview['snp_sl20'].change:+.2f})"
        )

        # Example 3: Top gainers
        print("\n🚀 Example 3: Top 5 Gainers")
        print("-" * 30)
        gainers = client.get_top_gainers()
        for i, gainer in enumerate(gainers[:5], 1):
            print(f"{i}. {gainer.symbol}: +{gainer.change_percentage:.2f}%")

        # Example 4: Top losers
        print("\n📉 Example 4: Top 5 Losers")
        print("-" * 30)
        losers = client.get_top_losers()
        for i, loser in enumerate(losers[:5], 1):
            print(f"{i}. {loser.symbol}: {loser.change_percentage:.2f}%")

        # Example 5: Most active trades
        print("\n💹 Example 5: Most Active Trades")
        print("-" * 30)
        active_trades = client.get_most_active_trades()
        for i, trade in enumerate(active_trades[:5], 1):
            print(f"{i}. {trade.symbol}: Volume {trade.trade_volume:,.0f}")

        # Example 6: Search companies
        print("\n🔍 Example 6: Search Companies")
        print("-" * 30)
        search_results = client.search_companies("BANK")
        print(f"Found {len(search_results)} companies with 'BANK' in symbol:")
        for result in search_results[:5]:  # Show first 5 results
            print(f"  {result.symbol}: LKR {result.last_traded_price}")

        # Example 7: Sectors information
        print("\n🏭 Example 7: Sector Information")
        print("-" * 30)
        sectors = client.get_all_sectors()
        for sector in sectors[:5]:  # Show first 5 sectors
            print(f"{sector.symbol}: {sector.index_name}")

    except CSEError as e:
        print(f"❌ CSE API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

    print("\n✅ Examples completed!")


def advanced_example():
    """Advanced usage with context manager and error handling."""
    print("\n🔧 Advanced Example: Context Manager & Error Handling")
    print("=" * 55)

    try:
        with CSEClient(timeout=60, max_retries=5) as client:
            # Get detailed market summary
            daily_summary = client.get_daily_market_summary()
            if daily_summary:
                latest = daily_summary[0]
                print(
                    f"📅 Latest Trading Day: {latest.trade_date.strftime('%Y-%m-%d')}"
                )
                print(f"💰 Market Turnover: LKR {latest.market_turnover:,.0f}")
                print(f"📊 Total Trades: {latest.trades_no:,}")
                print(f"🏢 Companies Traded: {latest.trade_company_number}")
                print(f"📈 ASPI: {latest.asi:.2f}")
                print(f"📉 S&P SL20: {latest.spp:.2f}")

            # Get announcements
            print("\n📢 Recent Financial Announcements:")
            financial_announcements = client.get_financial_announcements()
            for i, announcement in enumerate(financial_announcements[:3], 1):
                print(f"{i}. {announcement.company}")
                if announcement.file_text:
                    print(f"   📄 {announcement.file_text}")

    except CSEError as e:
        print(f"❌ CSE API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main()
    advanced_example()
