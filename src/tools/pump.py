from binance.client import Client

class CryptoPumpActivity:
    def __init__(self, binance_api_key, binance_api_secret):
        """Initializes the CryptoPumpActivity class with Binance API key and secret."""
        self.client = Client(binance_api_key, binance_api_secret)

    def get_pump_activity(self, symbol, interval='1d'):
        """Fetch pump activity data for a given cryptocurrency symbol and timeframe."""
        # Fetch historical klines (candlestick data) for the given timeframe
        klines = self.client.get_historical_klines(symbol, interval, "1 day ago UTC")
        
        # Extract closing prices and volume data
        price_open = float(klines[0][1])  # Opening price of the first candlestick
        price_close = float(klines[-1][4])  # Closing price of the last candlestick
        price_change_percent = ((price_close - price_open) / price_open) * 100  # Percentage change in price
        
        volume_open = float(klines[0][5])  # Volume from the first candlestick
        volume_close = float(klines[-1][5])  # Volume from the last candlestick
        volume_change_percent = ((volume_close - volume_open) / volume_open) * 100  # Volume percentage change
        
        result = {
            'symbol': symbol,
            'price_open': price_open,
            'price_close': price_close,
            'price_change_percent': price_change_percent,
            'volume_open': volume_open,
            'volume_close': volume_close,
            'volume_change_percent': volume_change_percent,
            'interval': interval
        }

        return result

# Example usage:
if __name__ == "__main__":
    binance_api_key = 'your_binance_api_key_here'
    binance_api_secret = 'your_binance_api_secret_here'
    pump_activity = CryptoPumpActivity(binance_api_key, binance_api_secret)
    symbol = 'HBARUSDT'  # Example symbol (change to any valid trading pair, e.g., HBAR/USDT)
    interval = '1h'  # Timeframe: '1m', '5m', '1h', '1d', etc.
    pump_data = pump_activity.get_pump_activity(symbol, interval)
    print(pump_data)
