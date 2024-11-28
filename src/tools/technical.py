import pandas as pd
from ta import add_all_ta_features
from ta.utils import dropna
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from binance.client import Client
from dotenv import load_dotenv
import os
import seaborn as sns

load_dotenv()

class MarketTrendAnalysis:
    def __init__(self, binance_api_key, binance_api_secret):
        """Initializes the MarketTrendAnalysis class with Binance API key and secret."""
        self.client = Client(binance_api_key, binance_api_secret)

    def get_historical_data(self, symbol, interval='4h', limit=500):
        """Fetch historical data for a specific cryptocurrency pair from Binance."""
        symbol += "USDT"
        klines = self.client.get_historical_klines(symbol, interval, limit=limit)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                           'close_time', 'quote_asset_volume', 'number_of_trades', 
                                           'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = pd.to_numeric(df['close'])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['volume'] = pd.to_numeric(df['volume'])
        df.set_index('timestamp', inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']]

    def calculate_technical_indicators(self, symbol):
        """Calculate various technical indicators: RSI, MACD, Bollinger Bands, etc."""
        """Calculate the support and resistance"""
        df = self.get_historical_data(symbol)
        df = dropna(df)
        df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
        df['MA50'] = df['close'].rolling(window=50).mean()
        indicator_bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_bbm'] = indicator_bb.bollinger_mavg()  # Bollinger Band Middle
        df['bb_bbh'] = indicator_bb.bollinger_hband()  # Bollinger Band High
        df['bb_bbl'] = indicator_bb.bollinger_lband()  # Bollinger Band Low
        df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()  # High Band Indicator
        df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()  # Low Band Indicator
        df['RSI'] = RSIIndicator(df['close'], window=14).rsi()
        df['MACD'] = MACD(df['close'], window_slow=26, window_fast=12, window_sign=9).macd()
        return df

    def plot_technical_indicators(self, df, output_file='technical_indicators.png'):
        """
<<<<<<< HEAD
        Plot the closing price along with technical indicators using Seaborn and export the graph as a PNG file.
=======
        Plot the closing price along with technical indicators and export the graph as a PNG file.
>>>>>>> e2100a24e84c69af311fb28e98f28ae8b3b2d96d

        Args:
            df (DataFrame): DataFrame containing crypto data with technical indicators.
            output_file (str): The filename for the exported PNG file.
        """
<<<<<<< HEAD
        sns.set(style="whitegrid")
        plt.figure(figsize=(16, 10))
=======
        plt.figure(figsize=(14, 8))
>>>>>>> e2100a24e84c69af311fb28e98f28ae8b3b2d96d

        # Check if Bollinger Bands are present in the DataFrame
        print("Columns in DataFrame:", df.columns)

<<<<<<< HEAD
        # Create the plot
        ax = sns.lineplot(x=df.index, y=df['close'], label='Close Price', color='black', linewidth=2)

        # Add Bollinger Bands
        if 'bb_bbm' in df.columns and 'bb_bbh' in df.columns and 'bb_bbl' in df.columns:
            sns.lineplot(x=df.index, y=df['bb_bbm'], label='Bollinger Band Middle', color='blue', linestyle='--')
            sns.lineplot(x=df.index, y=df['bb_bbh'], label='Bollinger Band High', color='green', linestyle='--')
            sns.lineplot(x=df.index, y=df['bb_bbl'], label='Bollinger Band Low', color='red', linestyle='--')

        # Add RSI
        if 'RSI' in df.columns:
            sns.lineplot(x=df.index, y=df['RSI'], label='RSI', color='orange', linestyle=':')
            plt.axhline(70, color='red', linestyle='--', linewidth=0.8, label='Overbought (70)')
            plt.axhline(30, color='green', linestyle='--', linewidth=0.8, label='Oversold (30)')

        # Add MACD
        if 'MACD' in df.columns:
            sns.lineplot(x=df.index, y=df['MACD'], label='MACD', color='purple', linestyle='-.')

        # Add titles and labels
        plt.title('Crypto Price and Technical Indicators', fontsize=16)
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Price and Indicators', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.tight_layout()
=======
        # Plot Closing Price and Bollinger Bands
        plt.plot(df['close'], label='Close Price', color='black', linewidth=1.5)
        if 'bb_bbm' in df.columns and 'bb_bbh' in df.columns and 'bb_bbl' in df.columns:
            plt.plot(df['bb_bbm'], label='Bollinger Band Middle', linestyle='--', color='blue')
            plt.plot(df['bb_bbh'], label='Bollinger Band High', linestyle='--', color='green')
            plt.plot(df['bb_bbl'], label='Bollinger Band Low', linestyle='--', color='red')

        # Add RSI (on a secondary y-axis)
        if 'RSI' in df.columns:
            plt.plot(df['RSI'], label='RSI', color='orange', linestyle=':', linewidth=1.5)
            plt.axhline(70, color='red', linestyle='--', linewidth=0.8)
            plt.axhline(30, color='green', linestyle='--', linewidth=0.8)

        # Add MACD
        if 'MACD' in df.columns:
            plt.plot(df['MACD'], label='MACD', color='purple', linestyle='-.', linewidth=1.5)

        plt.title('Crypto Price and Technical Indicators')
        plt.xlabel('Time')
        plt.ylabel('Price and Indicators')
        plt.legend()
        plt.grid(alpha=0.3)
>>>>>>> e2100a24e84c69af311fb28e98f28ae8b3b2d96d

        # Export to PNG
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot exported as {output_file}")

        # Show plot
        plt.show()

<<<<<<< HEAD

=======
    # def get_moving_average(self, df, window=50):
    #     """Get the moving average for a given window."""
    #     df_with_indicators = self.calculate_technical_indicators(df)
    #     return df_with_indicators[f'MA50'].iloc[-1]  # Return the last value of the moving average

    # def get_rsi(self, df):
    #     """Get the RSI for a given symbol."""
    #     df_with_indicators = self.calculate_technical_indicators(df)
    #     return df_with_indicators['RSI'].iloc[-1]

    # def get_macd(self, df):
    #     """Get the MACD for a given symbol."""
    #     df_with_indicators = self.calculate_technical_indicators(df)
    #     return df_with_indicators['MACD'].iloc[-1]

    # def get_support_resistance(self, df):
    #     """Get the support and resistance levels for a given cryptocurrency symbol."""
    #     df_with_indicators = self.calculate_technical_indicators(df)
    #     return {'support': df_with_indicators['bb_bbl'].iloc[-1], 'resistance': df_with_indicators['bb_bbh'].iloc[-1]}

    def get_price_prediction(self, df):
        """Predict the price for the next day using a trained machine learning model."""
        df_with_indicators = self.calculate_technical_indicators(df)
        
        # Train a Linear Regression model to predict the next day's closing price
        model = LinearRegression()
        df_with_indicators = df_with_indicators.dropna(subset=['bb_bbm', 'RSI', 'MACD'])
        X = df_with_indicators[['bb_bbm', 'RSI', 'MACD']].values
        y = df_with_indicators['close'].shift(-1).dropna().values  # Next day's price as the target
        X = X[:-1]  # Align X and y
        model.fit(X, y)

        # Predict the price for the next day
        latest_data = df_with_indicators[['bb_bbm', 'RSI', 'MACD']].iloc[-1].values.reshape(1, -1)
        predicted_price = model.predict(latest_data)[0]
        return predicted_price


# Example usage
>>>>>>> e2100a24e84c69af311fb28e98f28ae8b3b2d96d
if __name__ == "__main__":
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_API_SECRET")

    trend_analyzer = MarketTrendAnalysis(binance_api_key, binance_api_secret)
    symbol = 'BTC'  # Example symbol

    # Get Historical Data
    df = trend_analyzer.calculate_technical_indicators(symbol)
    # df = trend_analyzer.get_historical_data(symbol)

<<<<<<< HEAD
    trend_analyzer.plot_technical_indicators(df)

    # # Get Moving Average (MA50) for BTC
    # ma50 = trend_analyzer.get_moving_average(df, window=50)
    # print(f"50-Day Moving Average for {symbol}: {ma50:.2f}")

    # # Get RSI for BTC
    # rsi = trend_analyzer.get_rsi(df)
    # print(f"RSI for {symbol}: {rsi:.2f}")

    # # Get MACD for BTC
    # macd = trend_analyzer.get_macd(df)
    # print(f"MACD for {symbol}: {macd:.2f}")

    # # Get Support and Resistance for BTC
    # support_resistance = trend_analyzer.get_support_resistance(df)
    # print(f"Support level: {support_resistance['support']:.2f}, Resistance level: {support_resistance['resistance']:.2f}")

=======
    # Get Moving Average (MA50) for BTC
    # ma50 = trend_analyzer.get_moving_average(df, window=50)
    # print(f"50-Day Moving Average for {symbol}: {ma50:.2f}")

    # # Get RSI for BTC
    # rsi = trend_analyzer.get_rsi(df)
    # print(f"RSI for {symbol}: {rsi:.2f}")

    # # Get MACD for BTC
    # macd = trend_analyzer.get_macd(df)
    # print(f"MACD for {symbol}: {macd:.2f}")

    # # Get Support and Resistance for BTC
    # support_resistance = trend_analyzer.get_support_resistance(df)
    # print(f"Support level: {support_resistance['support']:.2f}, Resistance level: {support_resistance['resistance']:.2f}")

>>>>>>> e2100a24e84c69af311fb28e98f28ae8b3b2d96d
    # # Get Price Prediction for BTC
    # predicted_price = trend_analyzer.get_price_prediction(df)
    # print(f"Predicted price for {symbol} tomorrow: {predicted_price:.2f}")

