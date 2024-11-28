# tools.py

# from llama_index.core.tools import QueryEngineTool, ToolMetadata
# from binance.client import Client
# from src.tools.volume import get_top_volume_crypto,get_top_k_volume_crypto,get_price,get_top_10_volume_crypto, get_fear_and_greed_index
import os

from llama_index.core.tools import FunctionTool

from src.tools.news import CryptoNewsAggregator
from src.tools.pump import CryptoPumpActivity
from src.tools.technical import MarketTrendAnalysis
from src.tools.volume import CryptoData
from src.online_retriever.telegram import get_latest_posts
from src.tools.bitcoin_predict import BitcoinPredictor
from src.db.index import QdrantHandler

def create_query_engine_tools(
    binance_api_key,
    binance_api_secret,
    news_api_key,
    reddit_client_id,
    reddit_client_secret,
    reddit_user_agent="hello",
):  
    fed_data_path='dataset/interest_rate.xlsx'
    pump_instance = CryptoPumpActivity(binance_api_key, binance_api_secret)
    aggregator = CryptoNewsAggregator(
        news_api_key, reddit_client_id, reddit_client_secret, reddit_user_agent
    )
    analysis = MarketTrendAnalysis(binance_api_key, binance_api_secret)
    volumer = CryptoData(binance_api_key, binance_api_secret)
    
    bitcoin_predictor=BitcoinPredictor(binance_api_key, binance_api_secret, fed_data_path)


    get_top_k_volume_crypto_tool = FunctionTool.from_defaults(
        fn=lambda topk: volumer.get_top_k_usdt_volume_crypto(topk),
        name="get_top_volume_crypto_tool",
        description="A tool for retrieving top volume of trading pair in Binance",
    )
    get_fear_and_greed_index_tool = FunctionTool.from_defaults(
        fn=lambda: volumer.get_fear_and_greed_index(),
        name="get_fear_and_greed_index_tool",
        description="A tool for getting information about fear and greedy index",
    )
    get_price_tool = FunctionTool.from_defaults(
        fn=lambda symbol: volumer.get_price(symbol), name="get_price_tool"
    )
    get_volumes_for_symbols_tool = FunctionTool.from_defaults(
        fn=lambda symbol: volumer.get_volumes_for_symbols(symbol),
        name="get_volumes_for_symbols_tool",
        description="A tool for getting volume for single symbol",
    )

    get_pump_activity_tool = FunctionTool.from_defaults(
        fn=lambda symbol: pump_instance.get_pump_activity(symbol),
        name="get_pump_activity",
        description="A tool for tracking pump activity",
    )

    aggregate_news_tool = FunctionTool.from_defaults(
        fn=lambda keyword: aggregator.aggregate_news(keyword), name="get_news_tool",
        description="A tool for getting news from Google news and Reddit",
    )

    calculate_technical_indicators_tool = FunctionTool.from_defaults(
        fn=lambda keyword: analysis.calculate_technical_indicators(keyword),
        name="calculate_technical_indicators_tool",
        description="A tool for calculate the technical indicators",
    )

    telegram_get_latest_posts_tool = FunctionTool.from_defaults(
        fn=lambda channel_name: get_latest_posts(channel_name),
        name="telegram_get_latest_posts_tool",
        description="A tool for get news from telegram",
    )

    bitcoin_price_prediction_tool = FunctionTool.from_defaults(
        fn=lambda future_date: bitcoin_predictor.predict(future_date),
        name="bitcoin_price_prediction_tool",
        description="A tool to get interest FED rate, bitcoin price, halving date. Please use this information and give the prediction for bitcoin price at at certain date",
    )


    all_tools = [
        get_fear_and_greed_index_tool,
        get_top_k_volume_crypto_tool,
        get_price_tool,
        get_volumes_for_symbols_tool,
        get_pump_activity_tool,
        aggregate_news_tool,
        calculate_technical_indicators_tool,
        telegram_get_latest_posts_tool,
        bitcoin_price_prediction_tool
    ]

    return all_tools
