#!/usr/bin/env python3
"""
Advanced market analysis example using CSE.LK client.

This script demonstrates how to perform market analysis using the CSE API.
"""

import statistics
from datetime import datetime
from typing import List, Dict, Any

from cse_lk import CSEClient
from cse_lk.models import SharePrice
from cse_lk.exceptions import CSEError


class MarketAnalyzer:
    """Market analysis utilities using CSE data."""

    def __init__(self):
        self.client = CSEClient()

    def analyze_market_performance(self) -> Dict[str, Any]:
        """Analyze overall market performance."""
        try:
            # Get market overview
            overview = self.client.get_market_overview()

            # Get share prices for analysis
            share_prices = self.client.get_today_share_prices()

            # Calculate statistics
            prices = [
                price.last_traded_price
                for price in share_prices
                if price.last_traded_price > 0
            ]
            changes = [
                price.change_percentage
                for price in share_prices
                if price.change_percentage is not None
            ]

            positive_changes = [ch for ch in changes if ch > 0]
            negative_changes = [ch for ch in changes if ch < 0]

            analysis = {
                "market_status": overview["status"].status,
                "aspi": {
                    "value": overview["aspi"].value,
                    "change": overview["aspi"].change,
                },
                "snp_sl20": {
                    "value": overview["snp_sl20"].value,
                    "change": overview["snp_sl20"].change,
                },
                "statistics": {
                    "total_stocks": len(share_prices),
                    "stocks_with_prices": len(prices),
                    "average_price": statistics.mean(prices) if prices else 0,
                    "median_price": statistics.median(prices) if prices else 0,
                    "price_std_dev": statistics.stdev(prices) if len(prices) > 1 else 0,
                },
                "market_sentiment": {
                    "gainers": len(positive_changes),
                    "losers": len(negative_changes),
                    "unchanged": len(changes)
                    - len(positive_changes)
                    - len(negative_changes),
                    "avg_gain": (
                        statistics.mean(positive_changes) if positive_changes else 0
                    ),
                    "avg_loss": (
                        statistics.mean(negative_changes) if negative_changes else 0
                    ),
                    "market_breadth": (
                        len(positive_changes) / len(changes) if changes else 0
                    ),
                },
            }

            return analysis

        except CSEError as e:
            print(f"Error analyzing market: {e}")
            return {}

    def find_opportunities(self) -> Dict[str, List[SharePrice]]:
        """Find potential trading opportunities."""
        try:
            share_prices = self.client.get_today_share_prices()

            opportunities = {
                "high_volume_breakouts": [],
                "oversold_stocks": [],
                "strong_performers": [],
                "value_picks": [],
            }

            for price in share_prices:
                if not price.change_percentage:
                    continue

                # High percentage gainers with volume
                if (
                    price.change_percentage > 5.0
                    and price.volume
                    and price.volume > 10000
                ):
                    opportunities["strong_performers"].append(price)

                # Potential oversold (significant losers)
                elif price.change_percentage < -5.0:
                    opportunities["oversold_stocks"].append(price)

                # Value picks (low price, positive change)
                elif price.last_traded_price < 50 and price.change_percentage > 0:
                    opportunities["value_picks"].append(price)

            # Sort lists by change percentage
            for key in opportunities:
                if key == "oversold_stocks":
                    opportunities[key].sort(key=lambda x: x.change_percentage)
                else:
                    opportunities[key].sort(
                        key=lambda x: x.change_percentage, reverse=True
                    )

            return opportunities

        except CSEError as e:
            print(f"Error finding opportunities: {e}")
            return {}

    def sector_analysis(self) -> Dict[str, Any]:
        """Analyze sector performance."""
        try:
            sectors = self.client.get_all_sectors()

            sector_performance = []
            for sector in sectors:
                if sector.change_percentage is not None:
                    sector_performance.append(
                        {
                            "symbol": sector.symbol,
                            "name": sector.index_name,
                            "value": sector.value,
                            "change": sector.change,
                            "change_percentage": sector.change_percentage,
                        }
                    )

            # Sort by performance
            best_sectors = sorted(
                sector_performance, key=lambda x: x["change_percentage"], reverse=True
            )
            worst_sectors = sorted(
                sector_performance, key=lambda x: x["change_percentage"]
            )

            return {
                "best_performing": best_sectors[:5],
                "worst_performing": worst_sectors[:5],
                "total_sectors": len(sector_performance),
            }

        except CSEError as e:
            print(f"Error analyzing sectors: {e}")
            return {}


def main():
    """Main analysis function."""
    print("📊 CSE Market Analysis Report")
    print("=" * 50)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    analyzer = MarketAnalyzer()

    # Overall market analysis
    print("\n📈 Market Performance Analysis")
    print("-" * 40)

    market_analysis = analyzer.analyze_market_performance()
    if market_analysis:
        print(f"Market Status: {market_analysis['market_status']}")
        print(
            f"ASPI: {market_analysis['aspi']['value']:.2f} "
            f"({market_analysis['aspi']['change']:+.2f})"
        )
        print(
            f"S&P SL20: {market_analysis['snp_sl20']['value']:.2f} "
            f"({market_analysis['snp_sl20']['change']:+.2f})"
        )

        stats = market_analysis["statistics"]
        print("\n📊 Market Statistics:")
        print(f"  Total Stocks: {stats['total_stocks']}")
        print(f"  Average Price: LKR {stats['average_price']:.2f}")
        print(f"  Median Price: LKR {stats['median_price']:.2f}")
        print(f"  Price Volatility: {stats['price_std_dev']:.2f}")

        sentiment = market_analysis["market_sentiment"]
        print("\n💭 Market Sentiment:")
        print(f"  Gainers: {sentiment['gainers']} (+{sentiment['avg_gain']:.2f}% avg)")
        print(f"  Losers: {sentiment['losers']} ({sentiment['avg_loss']:.2f}% avg)")
        print(f"  Unchanged: {sentiment['unchanged']}")
        print(f"  Market Breadth: {sentiment['market_breadth']:.2%}")

    # Sector analysis
    print("\n🏭 Sector Performance")
    print("-" * 40)

    sector_analysis = analyzer.sector_analysis()
    if sector_analysis:
        print("🚀 Best Performing Sectors:")
        for i, sector in enumerate(sector_analysis["best_performing"], 1):
            print(f"  {i}. {sector['symbol']}: +{sector['change_percentage']:.2f}%")

        print("\n📉 Worst Performing Sectors:")
        for i, sector in enumerate(sector_analysis["worst_performing"], 1):
            print(f"  {i}. {sector['symbol']}: {sector['change_percentage']:.2f}%")

    # Trading opportunities
    print("\n💡 Trading Opportunities")
    print("-" * 40)

    opportunities = analyzer.find_opportunities()
    if opportunities:
        if opportunities["strong_performers"]:
            print("🚀 Strong Performers (>5% gain with volume):")
            for stock in opportunities["strong_performers"][:5]:
                print(
                    f"  {stock.symbol}: +{stock.change_percentage:.2f}% "
                    f"(Vol: {stock.volume:,})"
                )

        if opportunities["oversold_stocks"]:
            print("\n📉 Potentially Oversold (<-5% change):")
            for stock in opportunities["oversold_stocks"][:5]:
                print(f"  {stock.symbol}: {stock.change_percentage:.2f}%")

        if opportunities["value_picks"]:
            print("\n💎 Value Picks (Low price, positive change):")
            for stock in opportunities["value_picks"][:5]:
                print(
                    f"  {stock.symbol}: LKR {stock.last_traded_price:.2f} "
                    f"(+{stock.change_percentage:.2f}%)"
                )

    print("\n" + "=" * 50)
    print("⚠️  Disclaimer: This analysis is for educational purposes only.")
    print("   Always conduct your own research before making investment decisions.")


if __name__ == "__main__":
    main()
