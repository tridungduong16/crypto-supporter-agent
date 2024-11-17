# tools.py

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.tools import FunctionTool
from binance.client import Client
import os

def get_crypt_information(binance_api_key, binance_api_secret):
    """Get information about average price of BNBBTC pair"""
    binance_client = Client(binance_api_key, binance_api_secret)
    avg_price = binance_client.get_avg_price(symbol='BNBBTC')
    return avg_price

def create_query_engine_tools(binance_api_key, binance_api_secret):
    """Create and return a list of query engine tools."""
    multiply_tool = FunctionTool.from_defaults(fn=lambda: get_crypt_information(binance_api_key, binance_api_secret), name="crypto_tool")
    query_engine_tools = [
        QueryEngineTool(
            query_engine=None,  # Will be set dynamically later
            metadata=ToolMetadata(
                name="duong_tri_dung_information",
                description="Provide information about Duong Tri Dung"
            ),
        )
    ]
    all_tools = query_engine_tools + [multiply_tool]   
    return all_tools
