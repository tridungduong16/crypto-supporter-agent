# tools.py

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.tools import FunctionTool
from binance.client import Client
from src.tools.volume import get_top_volume_crypto,get_price,get_top_10_volume_crypto, get_fear_and_greed_index
import os

# def get_duong_tri_dung_information():
#     query_engine_tools = [
#         QueryEngineTool(
#             query_engine=None,  # Will be set dynamically later
#             metadata=ToolMetadata(
#                 name="duong_tri_dung_information",
#                 description="Provide information about Duong Tri Dung"
#             ),
#         )
#     ]
#     return query_engine_tools

def create_query_engine_tools(binance_api_key, binance_api_secret):
    get_top_10_volume_crypto_tool = FunctionTool.from_defaults(fn=lambda: get_top_10_volume_crypto(binance_api_key, binance_api_secret), name="get_top_10_volume_crypto_tool")
    get_fear_and_greed_index_tool = FunctionTool.from_defaults(fn=lambda: get_fear_and_greed_index(), name="get_fear_and_greed_index_tool")
    get_top_volume_crypto_tool = FunctionTool.from_defaults(fn=lambda: get_top_volume_crypto(), name="get_top_volume_crypto_tool")
    get_price_tool = FunctionTool.from_defaults(fn=lambda: get_price(), name="get_price_tool")

    # dtd_tool=get_duong_tri_dung_information()
    all_tools = [get_top_10_volume_crypto_tool, get_fear_and_greed_index_tool, get_top_volume_crypto_tool, get_price_tool]  
    return all_tools
