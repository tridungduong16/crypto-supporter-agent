from binance.client import Client
import os
from dotenv import load_dotenv
import requests
load_dotenv()

import requests
from binance.client import Client

def get_fear_and_greed_index():
    """ 
    Fetches the Crypto Fear & Greed Index from the Alternative.me API.
    
    This function makes a GET request to the Alternative.me API to retrieve the current
    Fear & Greed Index for the crypto market. It returns the index value and its sentiment
    classification (e.g., Extreme Fear, Fear, Neutral, Greed, or Extreme Greed).
    
    Returns:
        tuple: A tuple containing the Fear & Greed Index value and sentiment classification.
               If the request fails, it returns (None, "Error fetching data").
    """
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)  # Sending GET request to the API endpoint
    if response.status_code == 200:  # Check if the request was successful (HTTP 200 OK)
        data = response.json()  # Parse the response JSON into a Python dictionary
        index = data['data'][0]['value']  # Extract the Fear & Greed Index value
        sentiment = data['data'][0]['value_classification']  # Extract the sentiment classification
        return index, sentiment  # Return the index and sentiment classification
    else:
        return None, "Error fetching data"  # Return error message if the request fails


def get_top_volume_crypto(binance_api_key, binance_api_secret):
    """
    Retrieves the crypto pair with the highest 24-hour trading volume from Binance.

    This function connects to the Binance API using the provided API key and secret,
    fetches the trading data for all available pairs, and identifies the pair with the
    highest 24-hour trading volume.

    Args:
        binance_api_key (str): The API key for Binance account.
        binance_api_secret (str): The API secret for Binance account.

    Returns:
        tuple: The symbol of the pair with the highest trading volume and its volume.
    """
    binance_client = Client(binance_api_key, binance_api_secret)  # Initialize the Binance client
    tickers = binance_client.get_ticker()  # Get 24-hour price change statistics for all pairs
    top_volume_pair = None  # Variable to store the top volume pair
    top_volume = 0  # Variable to store the highest volume

    # Iterate through each ticker to find the pair with the highest volume
    for ticker in tickers:
        volume = float(ticker['volume'])  # Convert the volume to float
        if volume > top_volume:  # If the current pair's volume is higher than the stored one
            top_volume = volume  # Update the top volume
            top_volume_pair = ticker['symbol']  # Update the top volume pair

    return top_volume_pair, top_volume  # Return the pair with the highest volume and the volume


def get_top_10_volume_crypto(binance_api_key, binance_api_secret):
    """
    Retrieves the top 10 cryptocurrency pairs with the highest 24-hour trading volumes
    from Binance.

    This function connects to the Binance API using the provided API key and secret,
    fetches the trading data for all pairs, and sorts them by their trading volume in
    descending order to get the top 10 pairs with the highest volume.

    Args:
        binance_api_key (str): The API key for Binance account.
        binance_api_secret (str): The API secret for Binance account.

    Returns:
        list: A list of dictionaries containing the top 10 pairs and their respective volumes.
    """
    binance_client = Client(binance_api_key, binance_api_secret)  # Initialize the Binance client
    tickers = binance_client.get_ticker()  # Get 24-hour price change statistics for all pairs
    
    # Sort the tickers by volume in descending order (highest volume first)
    sorted_tickers = sorted(tickers, key=lambda x: float(x['volume']), reverse=True)
    
    top_10_pairs = []  # List to store the top 10 pairs and their volumes

    # Add the top 10 pairs to the list
    for i in range(10):
        top_10_pairs.append({
            'symbol': sorted_tickers[i]['symbol'],  # Add pair symbol
            'volume': sorted_tickers[i]['volume']   # Add the corresponding volume
        })

    return top_10_pairs  # Return the list of top 10 pairs


def get_crypto_information(binance_api_key, binance_api_secret):
    """
    Retrieves the average price of the BNBBTC pair from Binance.

    This function connects to the Binance API using the provided API key and secret,
    and fetches the average price for the BNBBTC trading pair.

    Args:
        binance_api_key (str): The API key for Binance account.
        binance_api_secret (str): The API secret for Binance account.

    Returns:
        float: The average price of the BNBBTC pair.
    """
    binance_client = Client(binance_api_key, binance_api_secret)  # Initialize the Binance client
    avg_price = binance_client.get_avg_price(symbol='BNBBTC')  # Get the average price for BNBBTC pair
    return avg_price  # Return the average price


BINANCE_API_KEY=os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET=os.getenv("BINANCE_API_SECRET")
top_pair, volume = get_top_volume_crypto(BINANCE_API_KEY, BINANCE_API_SECRET)
print(f"Top volume crypto pair: {top_pair} with volume: {volume}")
top_10_pairs = get_top_10_volume_crypto(BINANCE_API_KEY, BINANCE_API_SECRET)
print(f"Top volume crypto pair: {top_10_pairs}")
# Example usage
index, sentiment = get_fear_and_greed_index()
print(f"Fear & Greed Index: {index}, Sentiment: {sentiment}")
