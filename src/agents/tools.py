# tools.py

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.tools import FunctionTool
from binance.client import Client
from src.tools.volume import get_top_volume_crypto,get_top_k_volume_crypto,get_price,get_top_10_volume_crypto, get_fear_and_greed_index
import os
from src.tools.pump import CryptoPumpActivity
from src.tools.news import CryptoNewsAggregator




def create_query_engine_tools(binance_api_key, binance_api_secret, news_api_key, reddit_client_id, reddit_client_secret, reddit_user_agent='hello'):
    pump_instance=CryptoPumpActivity(binance_api_key, binance_api_secret)
    # aggregator = CryptoNewsAggregator(news_api_key, reddit_client_id, reddit_client_secret, reddit_user_agent)
    # news_api_key = '26456f944dc64ec78e15de90347b30fa'
    # reddit_client_id = 'NRixDNGtv1YZ0LSOx6HdMQ'
    # reddit_client_secret = 'FUehXZGuowSFtJpP5cBQXzRGFCJwtg'
    # reddit_user_agent = 'your_reddit_user_agent_here'
    aggregator = CryptoNewsAggregator(news_api_key, reddit_client_id, reddit_client_secret, reddit_user_agent)
    # aggregated_news = aggregator.aggregate_news('bitcoin')
    # print(aggregated_news)

    # print(news_api_key, reddit_client_id, reddit_client_secret, reddit_user_agent)

    get_top_k_volume_crypto_tool = FunctionTool.from_defaults(fn=lambda topk: get_top_k_volume_crypto(binance_api_key, binance_api_secret, topk), name="get_top_volume_crypto_tool")
    get_fear_and_greed_index_tool = FunctionTool.from_defaults(fn=lambda: get_fear_and_greed_index(), name="get_fear_and_greed_index_tool")
    get_pump_activity_tool = FunctionTool.from_defaults(fn=lambda symbol: pump_instance.get_pump_activity(symbol), name="get_pump_activity")
    get_price_tool = FunctionTool.from_defaults(fn=lambda symbol: get_price(binance_api_key, binance_api_secret, symbol), name="get_price_tool")
    aggregate_news_tool = FunctionTool.from_defaults(fn=lambda keyword: aggregator.aggregate_news(keyword), name="get_news_tool")

    
    all_tools = [get_fear_and_greed_index_tool, get_top_k_volume_crypto_tool, get_price_tool, get_pump_activity_tool, aggregate_news_tool]  
    return all_tools
