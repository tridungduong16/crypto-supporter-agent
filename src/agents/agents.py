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

        # DOCUMENTS = [
        #     Document(page_content="Duong Tri Dung\nPhone number: (+61) 411948899", metadata={"source": "tweet"}),
        #     Document(page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.", metadata={"source": "news"}),
        #     Document(page_content="Building an exciting new project with LangChain - come check it out!", metadata={"source": "tweet"}),
        #     # Document(page_content="Robbers broke into the city bank and stole $1 million in cash.", metadata={"source": "news"}),
        #     # Document(page_content="Wow! That was an amazing movie. I can't wait to see it again.", metadata={"source": "tweet"}),
        #     # Document(page_content="Is the new iPhone worth the price? Read this review to find out.", metadata={"source": "website"}),
        #     # Document(page_content="The top 10 soccer players in the world right now.", metadata={"source": "website"}),
        #     # Document(page_content="LangGraph is the best framework for building stateful, agentic applications!", metadata={"source": "tweet"}),
        #     # Document(page_content="The stock market is down 500 points today due to fears of a recession.", metadata={"source": "news"}),
        #     # Document(page_content="I have a bad feeling I am going to get deleted :(", metadata={"source": "tweet"}),
        # ]

        news_data = pd.read_csv("dataset/aggregated_news.csv")
        print(len(news_data))

        news_data = news_data.iloc[:5, :]

        # Convert each row to a Document object
        documents = [
            Document(
                page_content=(
                    f"{row.get('title', 'No title available')}\n"
                    f"{row.get('description', 'No description available')}\n"
                    f"Source: {row.get('source', 'Unknown source')}\n"
                    f"URL: {row.get('url', 'No URL available')}"
                ),
                metadata={"keyword": row.get("keyword", "Unknown keyword")}
            )
            for _, row in tqdm(news_data.iterrows(), total=news_data.shape[0])
        ]
        print(len(documents))

        qdrant_vector_store = QdrantVectorStore.from_documents(
            documents,
            embeddings,
            url=os.getenv("QDRANT_URL"),
            prefer_grpc=True,
            api_key=os.getenv("API_KEY_QDRANT"),
            collection_name=os.getenv("COLLECTION_NAME", "default_collection"),
        )
        retriever = qdrant_vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 10})


        # print("XXXXXXX")
        # res = (retriever.invoke("Duong Tri Dung"))
        # print(res)
        # print("XXXXXXX")
        # pdb.set_trace()retriever.invoke("Stealing from the bank is a crime")



        # retriever = qdrant_handler.vector_store
        self.retriever_tool = create_retriever_tool(
            retriever,
            name="retriever",
            description = "Retrieve latest news about cryptocurrency, crypto symbol from Google and Reddits",
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
        messages=self.print_stream(response)
        return messages