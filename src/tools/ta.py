import requests
import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv
import requests
load_dotenv()
import os

import requests
from binance.client import Client
load_dotenv()

class MarketTrendAnalysis:
    def __init__(self, binance_api_key, binance_api_secret):
        """Initializes the MarketTrendAnalysis class with Binance API key and secret."""
        self.client = Client(binance_api_key, binance_api_secret)

    def get_historical_data(self, symbol, interval='1d', limit=365):
        """Fetch historical data for a specific cryptocurrency pair from Binance."""
        klines = self.client.get_historical_klines(symbol, interval, limit=limit)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                           'close_time', 'quote_asset_volume', 'number_of_trades', 
                                           'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = pd.to_numeric(df['close'])
        df.set_index('timestamp', inplace=True)
        return df[['close']]

    def calculate_technical_indicators(self, df):
        """Calculate technical indicators: MA, RSI, MACD, Support/Resistance."""
        # Moving Average (MA)
        df['MA50'] = df['close'].rolling(window=50).mean()
        df['MA200'] = df['close'].rolling(window=200).mean()

        # Relative Strength Index (RSI)
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)

        # Moving Average Convergence Divergence (MACD)
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

        # Support/Resistance Levels (using rolling min/max for simplicity)
        df['Support'] = df['close'].rolling(window=50).min()
        df['Resistance'] = df['close'].rolling(window=50).max()

        return df

    def plot_technical_indicators(self, df):
        """Plot the closing price along with technical indicators: MA, RSI, MACD."""
        plt.figure(figsize=(14, 10))

        # Plot Closing Price and Moving Averages
        plt.subplot(3, 1, 1)
        plt.plot(df['close'], label='Close Price')
        plt.plot(df['MA50'], label='50-Day MA', linestyle='--')
        plt.plot(df['MA200'], label='200-Day MA', linestyle='--')
        plt.title('Crypto Price and Moving Averages')
        plt.legend()

        # Plot RSI
        plt.subplot(3, 1, 2)
        plt.plot(df['RSI'], label='RSI', color='orange')
        plt.axhline(70, color='red', linestyle='--')
        plt.axhline(30, color='green', linestyle='--')
        plt.title('Relative Strength Index (RSI)')
        plt.legend()

        # Plot MACD
        plt.subplot(3, 1, 3)
        plt.plot(df['MACD'], label='MACD', color='blue')
        plt.plot(df['MACD_signal'], label='MACD Signal', color='red')
        plt.bar(df.index, df['MACD_hist'], label='MACD Histogram', color='gray', alpha=0.5)
        plt.title('Moving Average Convergence Divergence (MACD)')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def get_moving_average(self, symbol, window=50):
        """Get the moving average for a given cryptocurrency symbol."""
        df = self.get_historical_data(symbol)
        df_with_indicators = self.calculate_technical_indicators(df)
        return df_with_indicators[f'MA{window}'].iloc[-1]  # Return the last value of the moving average

    def get_rsi(self, symbol):
        """Get the RSI for a given cryptocurrency symbol."""
        df = self.get_historical_data(symbol)
        df_with_indicators = self.calculate_technical_indicators(df)
        return df_with_indicators['RSI'].iloc[-1]

    def get_macd(self, symbol):
        """Get the MACD for a given cryptocurrency symbol."""
        df = self.get_historical_data(symbol)
        df_with_indicators = self.calculate_technical_indicators(df)
        return df_with_indicators['MACD'].iloc[-1]

    def get_support_resistance(self, symbol):
        """Get the support and resistance levels for a given cryptocurrency symbol."""
        df = self.get_historical_data(symbol)
        df_with_indicators = self.calculate_technical_indicators(df)
        return {'support': df_with_indicators['Support'].iloc[-1], 'resistance': df_with_indicators['Resistance'].iloc[-1]}

    def get_price_prediction(self, symbol):
        """Predict the price for the next day using a trained machine learning model."""
        df = self.get_historical_data(symbol)
        df_with_indicators = self.calculate_technical_indicators(df)
        
        # Train a Linear Regression model to predict the next day's closing price
        model = LinearRegression()
        df_with_indicators = df_with_indicators.dropna(subset=['MA50', 'MA200', 'RSI', 'MACD', 'MACD_signal'])
        X = df_with_indicators[['MA50', 'MA200', 'RSI', 'MACD', 'MACD_signal']].values
        y = df_with_indicators['close'].shift(-1).dropna().values  # Next day's price as the target
        X = X[:-1]  # Align X and y
        model.fit(X, y)

        # Predict the price for the next day
        latest_data = df_with_indicators[['MA50', 'MA200', 'RSI', 'MACD', 'MACD_signal']].iloc[-1].values.reshape(1, -1)
        predicted_price = model.predict(latest_data)[0]
        return predicted_price


# Example usage
if __name__ == "__main__":
    binance_api_key=os.getenv("BINANCE_API_KEY")
    binance_api_secret=os.getenv("BINANCE_API_SECRET")

    # binance_api_key = 'your_binance_api_key_here'
    # binance_api_secret = 'your_binance_api_secret_here'

    trend_analyzer = MarketTrendAnalysis(binance_api_key, binance_api_secret)
    symbol = 'BTCUSDT'  # Example symbol

    # Get Moving Average (MA50) for BTC
    ma50 = trend_analyzer.get_moving_average(symbol, window=50)
    print(f"50-Day Moving Average for {symbol}: {ma50:.2f}")

    # Get RSI for BTC
    rsi = trend_analyzer.get_rsi(symbol)
    print(f"RSI for {symbol}: {rsi:.2f}")

    # Get MACD for BTC
    macd = trend_analyzer.get_macd(symbol)
    print(f"MACD for {symbol}: {macd:.2f}")

    # Get Support and Resistance for BTC
    support_resistance = trend_analyzer.get_support_resistance(symbol)
    print(f"Support level: {support_resistance['support']:.2f}, Resistance level: {support_resistance['resistance']:.2f}")

    # Get Price Prediction for BTC
    predicted_price = trend_analyzer.get_price_prediction(symbol)
    print(f"Predicted price for {symbol} tomorrow: {predicted_price:.2f}")

    # Plot Technical Indicators
    df = trend_analyzer.get_historical_data(symbol)
    df_with_indicators = trend_analyzer.calculate_technical_indicators(df)
    trend_analyzer.plot_technical_indicators(df_with_indicators)
