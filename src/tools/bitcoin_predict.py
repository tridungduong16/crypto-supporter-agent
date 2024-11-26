import pandas as pd
from binance.client import Client
from datetime import datetime
import logging
from dotenv import load_dotenv
import os
import pdb
from datetime import datetime, timedelta
import numpy as np

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BitcoinPredictor:
    def __init__(self, binance_api_key, binance_api_secret, fed_data_path, proxies=None):
        """Initialize the predictor with Binance API credentials, FED data path, and proxies."""
        self.client = Client(binance_api_key, binance_api_secret)
        self.proxies = proxies
        self.fed_data_path = fed_data_path
        self.bitcoin_halving_dates = [
            "2012-11-28",  # First halving
            "2016-07-09",  # Second halving
            "2020-05-11",  # Third halving
            "2024-04-20",  # Fourth halving (Estimated)
            "2028-04-17",  # Fifth halving (Estimated)
            "2032-03-31",  # Sixth halving (Estimated)
            "2036-03-19",  # Seventh halving (Estimated)
            "2040-03-04",  # Eighth halving (Estimated)
        ]

    def get_historical_data(self, symbol, interval='1d', limit=5000):
        symbol += "USDT"
        klines = self.client.get_historical_klines(symbol, interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'number_of_trades', 
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = pd.to_numeric(df['close'])
        df.set_index('timestamp', inplace=True)
        return df[['close']]

    # def get_historical_data_longtime(self, symbol, interval='1d', limit=5000):
    def get_historical_data_longtime(self, symbol):
        """
        Load historical Bitcoin price data from a CSV file
        :return: A DataFrame containing Bitcoin's historical price data with Date as the index.
        """
        df = pd.read_csv("dataset/coinmarketcap.csv")
        df = df[df['Symbol'] == 'BTC']
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        df.set_index('Date', inplace=True)
        df = df[['Price']]
        df.rename(columns={'Price': 'close'}, inplace=True)
        return df


    def calculate_percentage_change(self, future_date, historical_data):
        """
        Calculate percentage change in Bitcoin price for a given future date, 
        comparing days since halving with historical data.

        :param future_date: The future date to predict (format: "YYYY-MM-DD").
        :param historical_data: A DataFrame containing Bitcoin's historical price data.
        :return: Percentage price change based on the nearest past halving date.
        """
        # Convert dates to datetime
        future_date_str = future_date
        future_date = datetime.strptime(future_date, "%Y-%m-%d")
        halving_dates = [datetime.strptime(date, "%Y-%m-%d") for date in self.bitcoin_halving_dates]
        halving_dates.sort()

        past_halving_date = max(date for date in halving_dates if date <= future_date)
        days_since_halving = (future_date - past_halving_date).days
        index_of_past_halving = halving_dates.index(past_halving_date)
        if index_of_past_halving == 0:  # No previous halving cycle
            raise ValueError("Not enough halving data to calculate comparison.")
        previous_halving_date = halving_dates[index_of_past_halving - 1]
        comparable_date = previous_halving_date + timedelta(days=days_since_halving)
        if comparable_date not in historical_data.index:
            comparable_date = historical_data.index[
                np.abs(historical_data.index - comparable_date).argmin()
            ]
        if previous_halving_date not in historical_data.index:
            previous_halving_date = historical_data.index[
                np.abs(historical_data.index - previous_halving_date).argmin()
            ]
        if past_halving_date not in historical_data.index:
            past_halving_date = historical_data.index[
                np.abs(historical_data.index - past_halving_date).argmin()
            ]
        previous_halving_price = historical_data.loc[previous_halving_date, 'close']
        past_halving_date = historical_data.loc[past_halving_date, 'close']

        comparable_price = historical_data.loc[comparable_date, 'close']
        percentage_change = ((comparable_price - previous_halving_price) / previous_halving_price) * 100

        # pdb.set_trace()

        # Calculate percentage change
        # percentage_change = ((future_price - comparable_price) / comparable_price) * 100
        return f"""
        There are {days_since_halving} days since the nearest halving.
        When comparing to previous period history, percentage price possibly increase/ decrease {percentage_change} from halving price. 
        Price of nearest halving date is {past_halving_date}. 
        """
    

    def load_fed_data(self):
        df = pd.read_excel(self.fed_data_path)
        df['Effective Date'] = pd.to_datetime(df['Effective Date'], format='%m/%d/%Y')
        df = df[df['Effective Date'] >= '2012-01-01']
        df_effr = df[df['Rate Type'] == 'EFFR']
        df_effr.set_index('Effective Date', inplace=True)
        numeric_df = df_effr.select_dtypes(include=['float64', 'int64'])
        monthly_avg_rates = numeric_df.resample('M').mean()
        logger.debug(f"Processed FED Data: {monthly_avg_rates.head()}")
        return monthly_avg_rates

    def get_bitcoin_cycle(self):
        """Calculate days since last Bitcoin halving and until the next one."""
        today = datetime.now()
        halving_dates = [datetime.strptime(date, "%Y-%m-%d") for date in self.bitcoin_halving_dates]
        halving_dates.sort()
        for i in range(len(halving_dates) - 1):
            if halving_dates[i] <= today < halving_dates[i + 1]:
                days_since_last = (today - halving_dates[i]).days
                days_until_next = (halving_dates[i + 1] - today).days
                return days_since_last, days_until_next
        return None, None
    

    def predict(self, future_date):
        """Predict Bitcoin price for a future date."""
        future_date_str = future_date
        future_date = datetime.strptime(future_date, "%Y-%m-%d").date()
        if future_date <= datetime.now().date():
            raise ValueError("Future date must be after today.")
        btc_data = self.get_historical_data("BTC")
        fed_data = self.load_fed_data()
        fed_data = fed_data[['Rate (%)']]

        btc_data_longtime = self.get_historical_data_longtime('Bitcoin')
        percentage_changes = self.calculate_percentage_change(future_date_str, btc_data_longtime)
        # pdb.set_trace()
        return {
            "FED average monthly rate interest data" : fed_data,
            "Bitcoin halving date": self.bitcoin_halving_dates,
            "Bitcoin price history": btc_data['close'],
            "future_date": future_date.strftime("%Y-%m-%d"),
            # "percentage_change": percentage_changes,
            # "past_halving_date": percentage_changes["past_halving_date"],
            # "comparable_date": percentage_changes["comparable_date"],
            # "future_price": percentage_changes["future_price"],
            # "comparable_price": percentage_changes["comparable_price"],
            # "percentage_change": percentage_changes["percentage_change"]
        }


# Initialize the predictor
binance_api_key = os.getenv("BINANCE_API_KEY")
binance_api_secret = os.getenv("BINANCE_API_SECRET")
fed_data_path = "dataset/interest_rate.xlsx"  # Path to your FED data TSV file
predictor = BitcoinPredictor(binance_api_key=binance_api_key, binance_api_secret=binance_api_secret, fed_data_path=fed_data_path)
predicted_price = predictor.predict("2025-05-01")
print(f"Predicted Bitcoin price: ${predicted_price}")
