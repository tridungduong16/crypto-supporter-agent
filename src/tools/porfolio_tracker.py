from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta

class PortfolioTracker:
    def __init__(self, api_key, api_secret, portfolio):
        """Initializes the Portfolio Tracker with API credentials and the user's portfolio."""
        self.client = Client(api_key, api_secret)
        self.portfolio = portfolio  # Portfolio format: {'BTC': 1.5, 'ETH': 10, 'XRP': 500}

    def get_live_price(self, symbol):
        """Fetches the live market price for a given cryptocurrency symbol."""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            return f"Error fetching live price for {symbol}: {e}"

    def calculate_portfolio_value(self):
        """Calculates the current total value of the portfolio in USD."""
        total_value = 0
        for symbol, amount in self.portfolio.items():
            price = self.get_live_price(symbol + "USDT")  # Convert symbol to USDT pair
            if isinstance(price, float):
                total_value += price * amount
        return total_value

    def calculate_gains_losses(self, timeframe='daily'):
        """Calculates the gains or losses for the portfolio over a specified timeframe (daily, weekly, monthly)."""
        current_value = self.calculate_portfolio_value()
        
        # Determine the date range for the timeframe
        if timeframe == 'daily':
            time_range = timedelta(days=1)
        elif timeframe == 'weekly':
            time_range = timedelta(weeks=1)
        elif timeframe == 'monthly':
            time_range = timedelta(weeks=4)
        else:
            return "Invalid timeframe"

        start_date = datetime.now() - time_range
        total_investment = 0

        # Get the portfolio value from start date to now (for historical comparison)
        for symbol, amount in self.portfolio.items():
            historical_price = self.get_historical_price(symbol + "USDT", start_date)
            if isinstance(historical_price, float):
                total_investment += historical_price * amount
        
        if total_investment == 0:
            return "Error in calculating gains/losses."

        # Calculate the gain or loss
        gains_losses = (current_value - total_investment) / total_investment * 100
        return round(gains_losses, 2)

    def get_historical_price(self, symbol, start_date):
        """Fetches the price of a given symbol on a specific date."""
        try:
            historical_data = self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, start_date.strftime("%d %b, %Y"))
            return float(historical_data[0][4])  # Closing price of the day
        except Exception as e:
            return f"Error fetching historical price for {symbol}: {e}"

    def portfolio_diversification(self):
        """Calculates portfolio diversification and provides risk management insights."""
        total_value = self.calculate_portfolio_value()
        diversification = {}

        for symbol, amount in self.portfolio.items():
            price = self.get_live_price(symbol + "USDT")
            if isinstance(price, float):
                asset_value = price * amount
                diversification[symbol] = {
                    'value': asset_value,
                    'percentage_of_total': (asset_value / total_value) * 100
                }

        return diversification

    def display_portfolio_summary(self):
        """Displays the portfolio's value, gains/losses, and diversification insights."""
        total_value = self.calculate_portfolio_value()
        st.write(f"**Total Portfolio Value**: ${total_value:.2f}")

        # Display gains and losses for different timeframes
        st.write(f"**Daily Gain/Loss**: {self.calculate_gains_losses('daily'):.2f}%")
        st.write(f"**Weekly Gain/Loss**: {self.calculate_gains_losses('weekly'):.2f}%")
        st.write(f"**Monthly Gain/Loss**: {self.calculate_gains_losses('monthly'):.2f}%")

        # Portfolio Diversification Insights
        diversification = self.portfolio_diversification()
        st.write(f"**Portfolio Diversification**:")
        for symbol, info in diversification.items():
            st.write(f"- {symbol}: ${info['value']:.2f} ({info['percentage_of_total']:.2f}%)")
            
        # Risk Management suggestion (example logic)
        if len(diversification) > 1:
            st.write("**Risk Management Suggestion**: Your portfolio has multiple assets, which reduces risk.")
        else:
            st.write("**Risk Management Suggestion**: Consider diversifying your portfolio to reduce risk.")

# Streamlit interface to interact with the portfolio tracker
import streamlit as st

st.title("Crypto Portfolio Tracker")

# Example portfolio: user can adjust this
portfolio = {'BTC': 1.5, 'ETH': 10, 'XRP': 500}  # Example portfolio

# Fetch API credentials (can also use `st.secrets`)
binance_api_key = "your_binance_api_key_here"
binance_api_secret = "your_binance_api_secret_here"

# Initialize the Portfolio Tracker
portfolio_tracker = PortfolioTracker(binance_api_key, binance_api_secret, portfolio)

# Display portfolio summary
portfolio_tracker.display_portfolio_summary()

