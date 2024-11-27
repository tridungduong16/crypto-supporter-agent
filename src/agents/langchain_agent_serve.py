from datetime import datetime
from typing import Optional, Annotated
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, START, StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_openai.llms.azure import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from src.tools.news import CryptoNewsAggregator
from src.tools.technical import MarketTrendAnalysis

class CryptoSupporterAgent:
    def __init__(self):
        # Initialize memory for persistent state tracking
        self.memory = MemorySaver()

        # Load environment variables
        load_dotenv()

        # Initialize configuration and components
        self._load_environment_variables()
        self._initialize_tools()
        self._initialize_model()
        self._initialize_graph()

    def _load_environment_variables(self):
        """Load and store environment variables."""
        self.collection_name = os.getenv("COLLECTION_NAME")
        self.data_path = os.getenv("DATA_PATH")
        self.model_name = os.getenv("MODEL_NAME")
        self.binance_api_key = os.getenv("BINANCE_API_KEY")
        self.binance_api_secret = os.getenv("BINANCE_API_SECRET")
        self.news_api_key = os.getenv("news_api_key")
        self.reddit_client_id = os.getenv("reddit_client_id")
        self.reddit_client_secret = os.getenv("reddit_client_secret")
        self.reddit_user_agent = "xxxxx"
        self.openai_api_key = os.getenv("openai_api_key")
        self.APIKEY_GPT4 = os.getenv("APIKEY_GPT4")
        self.AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
        self.API_VERSION = os.getenv("API_VERSION")
        self.OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")

    def _initialize_tools(self):
        """Initialize tools and their dependencies."""
        self.aggregator = CryptoNewsAggregator(
            self.news_api_key,
            self.reddit_client_id,
            self.reddit_client_secret,
            self.reddit_user_agent,
        )

        self.analysis = MarketTrendAnalysis(
            self.binance_api_key,
            self.binance_api_secret,
        )

        self.search_tool = DuckDuckGoSearchRun()

        self.tools = [
            self.aggregator.aggregate_news,
            self.analysis.calculate_technical_indicators,
            self.search_tool,
        ]

    def _initialize_model(self):
        """Initialize the AI model and bind tools."""
        # self.model = ChatOpenAI(model="gpt-4o", api_key=self.openai_api_key)
        self.model = AzureChatOpenAI(azure_endpoint=self.AZURE_ENDPOINT, 
                                 deployment_name=self.OPENAI_ENGINE,
                                 openai_api_key=self.APIKEY_GPT4,
                                 openai_api_version=self.API_VERSION)

        self.llm_with_tools = self.model.bind_tools(self.tools)

        self.system_prompt = """
        You are designed to help with a variety of tasks, from answering questions \
        to providing summaries to other types of analyses.

        You have access to a wide variety of tools. You are responsible for using
        the tools in any sequence you deem appropriate to complete the task at hand.
        This may require breaking the task into subtasks and using different tools
        to complete each subtask.
        """
        self.sys_msg = SystemMessage(content=self.system_prompt)

    def _initialize_graph(self):
        """Build and compile the state graph with memory."""
        self.builder = StateGraph(MessagesState)

        # Add nodes
        self.builder.add_node("reasoner", self._reasoner)
        self.builder.add_node("tools", ToolNode(self.tools))

        # Add edges
        self.builder.add_edge(START, "reasoner")
        self.builder.add_conditional_edges("reasoner", tools_condition)
        self.builder.add_edge("tools", "reasoner")
        self.builder.add_edge("reasoner", END)  # Mark the end of the process

        # Compile the graph with memory integration
        self.react_graph = self.builder.compile(checkpointer=self.memory)

    def _reasoner(self, state: MessagesState):
        """Reasoner function that processes messages."""
        return {"messages": [self.llm_with_tools.invoke([self.sys_msg] + state["messages"])]}

    def process_message(self, message: str):
        """Process a single user message through the graph."""
        config = {"configurable": {"thread_id": "1"}}
        response = self.react_graph.stream(
            {"messages": [("user", message)]}, config, stream_mode="values"
        )
        for event in response:
            event["messages"][-1].pretty_print()


# if __name__ == "__main__":
#     agent = CryptoSupporterAgent()
#     initial_message = "Get technical analysis for BTC"
#     agent.process_message(initial_message)
#     initial_message = "How about news for it?"
#     agent.process_message(initial_message)
#     initial_message = "Search for information about Solana"
#     agent.process_message(initial_message)