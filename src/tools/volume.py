import os

import requests
from binance.client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CryptoData:
    def __init__(self, binance_api_key, binance_api_secret):
        # self.binance_api_key = binance_api_key
        # self.binance_api_secret = binance_api_secret
        self.binance_client = Client(binance_api_key, binance_api_secret)

    def get_fear_and_greed_index(self):
        """
        Fetches the Crypto Fear & Greed Index from the Alternative.me API.
        """
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            index = data["data"][0]["value"]
            sentiment = data["data"][0]["value_classification"]
            return index, sentiment
        return None, "Error fetching data"

    def get_bitcoin_dominance(self):
        """
        Fetches the Bitcoin dominance percentage from the CoinGecko API.
        """
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            dominance = data["data"]["market_cap_percentage"]["btc"]
            return dominance
        return None

    def get_total_market_cap(self):
        """
        Fetches the total cryptocurrency market capitalization from CoinGecko API.
        """
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["total_market_cap"]["usd"]
        return None

    def get_top_10_cryptos_by_market_cap(self):
        """
        Fetches the top 10 cryptocurrencies by market capitalization from CoinGecko API.
        """
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "name": coin["name"],
                    "symbol": coin["symbol"],
                    "market_cap": coin["market_cap"],
                }
                for coin in data
            ]
        return []

    def get_top_volume_crypto(self):
        """
        Retrieves the crypto pair with the highest 24-hour trading volume from Binance.
        """
        tickers = self.binance_client.get_ticker()
        top_volume_pair = max(tickers, key=lambda x: float(x["volume"]))
        return top_volume_pair["symbol"], float(top_volume_pair["volume"])

    def get_top_10_volume_crypto(self):
        """
        Retrieves the top 10 cryptocurrency pairs with the highest 24-hour trading volumes from Binance.
        """
        tickers = self.binance_client.get_ticker()
        sorted_tickers = sorted(tickers, key=lambda x: float(x["volume"]), reverse=True)
        return [
            {"symbol": ticker["symbol"], "volume": float(ticker["volume"])}
            for ticker in sorted_tickers[:10]
        ]

    def get_price(self, symbol):
        """
        Retrieves the average price of the given trading pair from Binance.
        """
        avg_price = self.binance_client.get_avg_price(symbol=symbol)
        return avg_price

    def get_single_symbol_volume(self, symbol):
        """
        Retrieves the 24-hour trading volume for a single cryptocurrency pair from Binance.
        """
        try:
            ticker = self.binance_client.get_ticker(symbol=symbol)
            return {"symbol": ticker["symbol"], "volume": float(ticker["volume"])}
        except Exception as e:
            return {"error": str(e)}

    def get_highest_volume_symbol(self):
        """
        Retrieves the cryptocurrency pair with the highest 24-hour trading volume from Binance.
        """
        tickers = self.binance_client.get_ticker()
        highest_volume = max(tickers, key=lambda x: float(x["volume"]))
        return {
            "symbol": highest_volume["symbol"],
            "volume": float(highest_volume["volume"]),
        }

    def get_lowest_volume_symbol(self):
        """
        Retrieves the cryptocurrency pair with the lowest 24-hour trading volume from Binance.
        """
        tickers = self.binance_client.get_ticker()
        lowest_volume = min(tickers, key=lambda x: float(x["volume"]))
        return {
            "symbol": lowest_volume["symbol"],
            "volume": float(lowest_volume["volume"]),
        }

    def get_total_market_volume(self):
        """
        Calculates the total 24-hour trading volume across all cryptocurrency pairs from Binance.
        """
        tickers = self.binance_client.get_ticker()
        total_volume = sum(float(ticker["volume"]) for ticker in tickers)
        return total_volume

    def get_top_n_volume_contributors(self, n=10):
        """
        Retrieves the top N cryptocurrency pairs contributing the most to the total market volume from Binance.
        """
        tickers = self.binance_client.get_ticker()
        sorted_tickers = sorted(tickers, key=lambda x: float(x["volume"]), reverse=True)
        return [
            {"symbol": ticker["symbol"], "volume": float(ticker["volume"])}
            for ticker in sorted_tickers[:n]
        ]

    def get_volumes_for_symbols(self, symbols):
        """
        Retrieves 24-hour trading volumes for a list of cryptocurrency pairs from Binance.
        """
        tickers = self.binance_client.get_ticker()
        volume_data = []
        for symbol in symbols:
            symbol_ticker = next(
                (ticker for ticker in tickers if ticker["symbol"] == symbol), None
            )
            if symbol_ticker:
                volume_data.append(
                    {
                        "symbol": symbol_ticker["symbol"],
                        "volume": float(symbol_ticker["volume"]),
                    }
                )
            else:
                volume_data.append({"symbol": symbol, "error": "Not found"})
        return volume_data

    def get_top_k_volume_crypto(self, topk=10):
        """
        Retrieves the top k cryptocurrency pairs with the highest 24-hour trading volumes
        from Binance.

        This function connects to the Binance API using the provided API key and secret,
        fetches the trading data for all pairs, and sorts them by their trading volume in
        descending order to get the top k pairs with the highest volume.

        Args:
            binance_api_key (str): The API key for Binance account.
            binance_api_secret (str): The API secret for Binance account.

        Returns:
            list: A list of dictionaries containing the top 10 pairs and their respective volumes.
        """
        tickers = (
            self.binance_client.get_ticker()
        )  # Get 24-hour price change statistics for all pairs
        sorted_tickers = sorted(tickers, key=lambda x: float(x["volume"]), reverse=True)
        top_10_pairs = []  # List to store the top 10 pairs and their volumes
        for i in range(topk):
            top_10_pairs.append(
                {
                    "symbol": sorted_tickers[i]["symbol"],  # Add pair symbol
                    "volume": sorted_tickers[i][
                        "volume"
                    ],  # Add the corresponding volume
                }
            )
        return top_10_pairs

    def get_top_k_usdt_volume_crypto(self, topk=10):
        """
        Retrieves the top k cryptocurrency pairs with the highest 24-hour trading volumes
        in USDT from Binance.

        This function connects to the Binance API using the provided client,
        fetches the trading data for all pairs, filters pairs that are traded against USDT,
        and calculates the volume in USDT by multiplying the token volume by its last price.

        Args:
            topk (int): The number of top pairs to retrieve (default is 10).

        Returns:
            list: A list of dictionaries containing the top k USDT pairs and their respective USDT volumes.
        """
        # Get 24-hour price change statistics for all pairs
        tickers = self.binance_client.get_ticker()

        # Filter for pairs traded against USDT
        usdt_tickers = [
            ticker for ticker in tickers if ticker["symbol"].endswith("USDT")
        ]

        # Calculate the volume in USDT and add it to each ticker
        for ticker in usdt_tickers:
            ticker["usdt_volume"] = float(ticker["volume"]) * float(ticker["lastPrice"])

        # Sort the USDT pairs by the calculated USDT volume in descending order
        sorted_usdt_tickers = sorted(
            usdt_tickers, key=lambda x: float(x["usdt_volume"]), reverse=True
        )

        # Get the top k pairs
        top_usdt_pairs = []
        for i in range(min(topk, len(sorted_usdt_tickers))):
            top_usdt_pairs.append(
                {
                    "symbol": sorted_usdt_tickers[i]["symbol"],  # Add pair symbol
                    "usdt_volume": sorted_usdt_tickers[i][
                        "usdt_volume"
                    ],  # Add the calculated USDT volume
                }
            )

        return top_usdt_pairs


# Example usage:
# crypto_data = CryptoData()
# print(crypto_data.get_fear_and_greed_index())
# print(crypto_data.get_bitcoin_dominance())
# print(crypto_data.get_total_market_cap())
# print(crypto_data.get_top_10_volume_crypto())
# print(crypto_data.get_single_symbol_volume("BTCUSDT"))
