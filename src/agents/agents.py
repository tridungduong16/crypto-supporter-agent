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
from langchain_core.messages.ai import AIMessage
import pdb
from src.tools.volume import CryptoData
from src.db.index import QdrantHandler
from langchain_core.documents import Document
from langchain.tools.retriever import create_retriever_tool
from langchain_huggingface import HuggingFaceEmbeddings
from uuid import uuid4
from langchain_qdrant import QdrantVectorStore
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from PyPDF2 import PdfReader
from uuid import uuid4
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool, tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from IPython.display import Image, display

class CryptoSupporterAgent:
    def __init__(self):

        self.memory = MemorySaver()

        load_dotenv()

        self._load_environment_variables()
        self._initialize_model()
        self._initialize_tools()
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
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

    def _initialize_tools(self):
        retriever = self.qdrant_vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 10}
        )

        self.retriever_tool = create_retriever_tool(
            retriever,
            name="retriever",
            description="Retrieve information about duong tri dung",
        )

        self.search_tool = DuckDuckGoSearchRun()
        self.tools = [
            self.aggregator.aggregate_news,
            self.analysis.calculate_technical_indicators,
            self.search_tool,
            self.volumer.get_volumes_for_symbols,
            self.volumer.get_top_k_usdt_volume_crypto,
            self.volumer.get_fear_and_greed_index,
            self.retriever_tool,
            self.plot_chart,
            self.analysis.get_historical_data
        ]
        self.llm_with_tools = self.model.bind_tools(self.tools)

    def _initialize_model(self):
        """Initialize the AI model and bind tools."""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu", "trust_remote_code": True},
        )
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"), api_key=os.getenv("API_KEY_QDRANT")
        )

        self.qdrant_vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=os.getenv("COLLECTION_NAME", "default_collection"),
            embedding=self.embeddings,
        )

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

        self.volumer = CryptoData(
            self.binance_api_key,
            self.binance_api_secret,
        )

        self.model = AzureChatOpenAI(
            azure_endpoint=self.AZURE_ENDPOINT,
            deployment_name=self.OPENAI_ENGINE,
            openai_api_key=self.APIKEY_GPT4,
            openai_api_version=self.API_VERSION,
        )


        self.system_prompt = """

            You are a highly knowledgeable and resourceful cryptocurrency agent designed to assist with a variety of tasks, ranging from answering questions to providing summaries, conducting technical analyses, and aggregating relevant information about the cryptocurrency market.

            You have access to a wide array of tools and resources, including those tailored for retrieving cryptocurrency news, analyzing market trends, and generating insights. You are responsible for utilizing these tools in any sequence necessary to effectively complete the tasks assigned to you. This may involve breaking the task into smaller subtasks and using the appropriate tools for each subtask.

            When users ask about news or updates, you must include URLs as references to ensure transparency and credibility. Additionally, your responses should be tailored to the cryptocurrency context, offering detailed, accurate, and actionable insights whenever possible.

            If a user’s question or request is unclear, you should proactively ask clarification questions to better understand their needs. For example:
            - If a user says, "Give me information," respond with, "Could you clarify what cryptocurrency or topic you’re interested in, such as Bitcoin, Ethereum, or another area?"
            - If a user asks, "What’s the latest news?" without specifics, ask, "What cryptocurrency or market sector would you like news about?"
            - If the user requests a summary, ask, "Are you looking for a technical analysis, recent news, or general market trends?"

            Similarly, if the task requires deeper exploration, you should ask thoughtful follow-up questions to gather additional context and provide more comprehensive support. For example:
            - If a user asks about investment advice, you might ask, "Are you looking for insights on long-term trends or short-term trading opportunities?"
            - If a user asks for technical indicators, follow up with, "Would you like specific metrics like RSI, MACD, or Bollinger Bands?"

            After completing a topic, encourage the user to explore more by suggesting related topics or areas of interest. For example:
            - If a user asks about Bitcoin news, you could follow up with, "Do you want to know more about Ethereum or other trending cryptocurrencies?"
            - If a user inquires about technical analysis, you might ask, "Would you like me to explain how these indicators are calculated or show you analysis for another coin?"

            Your ultimate goal is to provide helpful, reliable, and user-centered support to those seeking information and guidance in the cryptocurrency space. Be conversational, empathetic, and thorough in your responses, ensuring that users feel supported and informed while inviting them to discover new topics or areas of interest.
        """
        self.sys_msg = SystemMessage(content=self.system_prompt)
        self.config = {"configurable": {"thread_id": "1"}}


    def plot_chart(self, dataframe) -> None:
        """
        Generates and saves a line chart based on the given dataframe.

        The function plots the "close" column of the dataframe against its index, 
        formats the chart with labels, a title, and gridlines, and saves the 
        resulting image as "123.png" in the current directory.

        Parameters:
        ----------
        dataframe : pandas.DataFrame
            The input dataframe containing the data to plot. It should have:
            - An index representing the x-axis (e.g., dates).
            - A column named "close" representing the y-axis values.

        Returns:
        -------
        None
            The function saves the chart as a PNG file and does not return any value.

        Side Effects:
        -------------
        - A file named "123.png" is saved in the current directory.
        - A message indicating the file's save location is printed to the console.

        Example:
        --------
        >>> import pandas as pd
        >>> data = {'close': [100, 110, 105, 115]}
        >>> df = pd.DataFrame(data, index=["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])
        >>> my_object = MyClass()
        >>> my_object.plot_chart(df)
        Your chart is saved as 123.png
        """
        x_axis, y_axis = dataframe.index, dataframe['close']
        plt.figure(figsize=(10, 5))
        plt.plot(x_axis, y_axis, marker="o")
        plt.title("Price History")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        path = "123.png"
        plt.savefig(path)
        plt.close()
        print(f"Your chart is saved as {path}")


    def _initialize_graph(self):
        """Build and compile the state graph with memory."""
        self.builder = StateGraph(MessagesState)
        self.builder.add_node("reasoner", self._reasoner)
        self.builder.add_node("tools", ToolNode(self.tools))
       
        self.builder.add_edge(START, "reasoner")
        self.builder.add_conditional_edges("reasoner", tools_condition)
        self.builder.add_edge("tools", "reasoner")
        self.builder.add_edge("reasoner", END)

        # Compile the graph with memory integration
        self.react_graph = self.builder.compile(checkpointer=self.memory)

        output_path = "diagram.png"  # Specify the file path to save the image
        try:
            image = Image(self.react_graph.get_graph(xray=True).draw_mermaid_png())            
            display(image)
            with open(output_path, "wb") as f:
                f.write(image.data)
            print(f"Diagram saved to {output_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
            


    def _reasoner(self, state: MessagesState):
        """Reasoner function that processes messages."""
        return {
            "messages": [self.llm_with_tools.invoke([self.sys_msg] + state["messages"])]
        }

    def get_last_ai_message_content(self, response):
        last_ai_message_content = ""
        for event in response:
            for message in event.get("messages", []):
                if isinstance(message, AIMessage):
                    last_ai_message_content = message.content
        return last_ai_message_content

    def print_stream(self, stream):
        last_ai_message_content = ""
        for s in stream:
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

            for message in s.get("messages", []):
                if isinstance(message, AIMessage):
                    last_ai_message_content = message.content
        return last_ai_message_content

    def process_message(self, message: str):
        response = self.react_graph.stream(
            {"messages": [("user", message)]}, self.config, stream_mode="values"
        )
        messages = self.print_stream(response)
        return messages