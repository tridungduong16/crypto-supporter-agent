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
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

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

        self.volumer = CryptoData(self.binance_api_key, self.binance_api_secret,)
        qdrant_handler=QdrantHandler()

        model_kwargs = {"device": "cpu", "trust_remote_code": True}

        embeddings = HuggingFaceEmbeddings(
                    model_name=self.embedding_model_name, model_kwargs=model_kwargs
                )



        # qdrant = QdrantVectorStore.from_existing_collection(
        #     embedding=embeddings,
        #     collection_name=os.getenv("COLLECTION_NAME", "default_collection"),
        #     url="http://localhost:6333",
        # )

        DOCUMENTS = [
            Document(page_content="Duong Tri Dung\nPhone number: (+61) 411948899", metadata={"source": "tweet"}),
            Document(page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.", metadata={"source": "news"}),
            Document(page_content="Building an exciting new project with LangChain - come check it out!", metadata={"source": "tweet"}),
            # Document(page_content="Robbers broke into the city bank and stole $1 million in cash.", metadata={"source": "news"}),
            # Document(page_content="Wow! That was an amazing movie. I can't wait to see it again.", metadata={"source": "tweet"}),
            # Document(page_content="Is the new iPhone worth the price? Read this review to find out.", metadata={"source": "website"}),
            # Document(page_content="The top 10 soccer players in the world right now.", metadata={"source": "website"}),
            # Document(page_content="LangGraph is the best framework for building stateful, agentic applications!", metadata={"source": "tweet"}),
            # Document(page_content="The stock market is down 500 points today due to fears of a recession.", metadata={"source": "news"}),
            # Document(page_content="I have a bad feeling I am going to get deleted :(", metadata={"source": "tweet"}),
        ]
        # qdrant_handler.index_documents(DOCUMENTS)
        qdrant_vector_store = QdrantVectorStore.from_documents(
            DOCUMENTS,
            embeddings,
            url=os.getenv("QDRANT_URL"),
            prefer_grpc=True,
            api_key=os.getenv("API_KEY_QDRANT"),
            collection_name=os.getenv("COLLECTION_NAME", "default_collection"),
        )
        retriever = qdrant_vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 1})


        # print("XXXXXXX")
        # res = (retriever.invoke("Duong Tri Dung"))
        # print(res)
        # print("XXXXXXX")
        # pdb.set_trace()retriever.invoke("Stealing from the bank is a crime")



        # retriever = qdrant_handler.vector_store
        self.retriever_tool = create_retriever_tool(
            retriever,
            name="retriever",
            description = "Retrieve information about Duong Tri Dung",
        )

        # self.retriever_tool = qdrant_handler.retriever_tool
        self.search_tool = DuckDuckGoSearchRun()
        self.tools = [
            self.aggregator.aggregate_news,
            self.analysis.calculate_technical_indicators,
            self.search_tool,
            self.volumer.get_volumes_for_symbols,
            self.volumer.get_top_k_usdt_volume_crypto,
            self.volumer.get_fear_and_greed_index,
            self.retriever_tool 
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
        self.config = {"configurable": {"thread_id": "1"}}

    def _initialize_graph(self):
        """Build and compile the state graph with memory."""
        self.builder = StateGraph(MessagesState)

        # Add nodes
        self.builder.add_node("reasoner", self._reasoner)
        # self.builder.add_node("retrieve_qdrant", ToolNode([self.retriever_tool]))
        self.builder.add_node("tools", ToolNode(self.tools))

        # Add edges
        self.builder.add_edge(START, "reasoner")
        self.builder.add_conditional_edges("reasoner", tools_condition)
        self.builder.add_edge("tools", "reasoner")
        # self.builder.add_edge("retrieve_qdrant", "reasoner")  # Add edge for retriever node
        self.builder.add_edge("reasoner", END)  # Mark the end of the process

        # Compile the graph with memory integration
        self.react_graph = self.builder.compile(checkpointer=self.memory)

    def _reasoner(self, state: MessagesState):
        """Reasoner function that processes messages."""
        return {"messages": [self.llm_with_tools.invoke([self.sys_msg] + state["messages"])]}

    def get_last_ai_message_content(self, response):
        """
        Extracts the content of the last AIMessage from a generator of response events.

        Args:
            response (generator): A generator containing response events.

        Returns:
            str: Content of the last AIMessage or an empty string if not found.
        """
        last_ai_message_content = ""
        for event in response:
            # Iterate through the messages in the event
            for message in event.get("messages", []):
                if isinstance(message, AIMessage):
                    last_ai_message_content = message.content  # Update with the latest AIMessage content
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
                    last_ai_message_content = message.content  # Update with the latest AIMessage content
        return last_ai_message_content
    
    def process_message(self, message: str):
        """Process a single user message through the graph."""
        response = self.react_graph.stream(
            {"messages": [("user", message)]}, self.config, stream_mode="values"
        )
        # self.print_stream(response)
        messages=self.print_stream(response)
        return messages