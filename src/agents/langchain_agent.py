from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

from src.tools.news import CryptoNewsAggregator
from src.tools.pump import CryptoPumpActivity
from src.tools.technical import MarketTrendAnalysis
from src.tools.volume import CryptoData
from src.online_retriever.telegram import get_latest_posts
from src.tools.bitcoin_predict import BitcoinPredictor
import pdb


class CryptoSupporterAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Initialize configuration and tools
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
        ]

    def _initialize_model(self):
        """Initialize the AI model and bind tools."""
        self.model = ChatOpenAI(model="gpt-4o", api_key=self.openai_api_key)
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
        """Build and compile the state graph."""
        self.builder = StateGraph(MessagesState)

        # Add nodes
        self.builder.add_node("reasoner", self._reasoner)
        self.builder.add_node("tools", ToolNode(self.tools))

        # Add edges
        self.builder.add_edge(START, "reasoner")
        self.builder.add_conditional_edges("reasoner", tools_condition)
        self.builder.add_edge("tools", "reasoner")

        # Compile the graph
        self.react_graph = self.builder.compile()

    def _reasoner(self, state: MessagesState):
        """Reasoner function that processes messages."""
        return {"messages": [self.llm_with_tools.invoke([self.sys_msg] + state["messages"])]}

    def process_messages(self, messages: list):
        """Process a list of messages through the graph."""
        state = {"messages": messages}
        response = self.react_graph.invoke(state)
        for message in response["messages"]:
            message.pretty_print()
        return response

    def interactive_session(self):
        """Run an interactive session for testing."""
        messages = [HumanMessage(content="Get technical analysis for BTC")]
        self.process_messages(messages)
        messages = [HumanMessage(content="How about news for it?")]
        self.process_messages(messages)


# Run the agent
if __name__ == "__main__":
    agent = CryptoSupporterAgent()
    agent.interactive_session()
