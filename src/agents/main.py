import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import StorageContext
from binance.client import Client
from llama_index.core.tools import FunctionTool

# Load environment variables from .env file
load_dotenv()

class AIApplication:
    def __init__(self, llm, 
                 qdrant_client, 
                 collection_name, 
                 data_path, 
                 model_name, 
                 binance_api_key, 
                 binance_api_secret):
        self.llm = llm
        Settings.llm = self.llm
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.qdrant_client.delete_collection(collection_name=self.collection_name)
        self.qdrant_client.create_collection(
            collection_name=self.collection_name, 
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        self.vector_store = QdrantVectorStore(client=self.qdrant_client, collection_name=self.collection_name)
        self.documents = SimpleDirectoryReader(data_path).load_data()
        self.embed_model = HuggingFaceEmbedding(model_name=model_name)
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_documents(self.documents, storage_context=storage_context, embed_model=self.embed_model)
    
        multiply_tool = FunctionTool.from_defaults(fn=self.get_crypt_information, name="crypto_tool")

        self.query_engine = self.index.as_query_engine(similarity_top_k=2)
        self.query_engine_tools = [
            QueryEngineTool(
                query_engine=self.query_engine,
                metadata=ToolMetadata(
                    name="duong_tri_dung_information",
                    description="Provide information about Duong Tri Dung"
                ),
            )
        ]
        all_tools = self.query_engine_tools + [multiply_tool]

        self.agent = OpenAIAgent.from_tools(all_tools, llm=self.llm, verbose=True)
        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret

    def get_crypt_information(self):
        """Get information about average price of BNBBTC pair"""
        binance_client = Client(self.binance_api_key, self.binance_api_secret)
        avg_price = binance_client.get_avg_price(symbol='BNBBTC')
        return avg_price

    def run(self):
        self.agent.chat_repl()


# Entry point
if __name__ == "__main__":
    BINANCE_API_KEY=os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET=os.getenv("BINANCE_API_SECRET")
    APIKEY_GPT4=os.getenv("APIKEY_GPT4")
    API_KEY_QDRANT=os.getenv("API_KEY_QDRANT")
    COLLECTION_NAME=os.getenv("COLLECTION_NAME")
    DATA_PATH=os.getenv("DATA_PATH")
    MODEL_NAME=os.getenv("MODEL_NAME")
    AZURE_ENDPOINT=os.getenv("AZURE_ENDPOINT")
    API_VERSION=os.getenv("API_VERSION")
    QDRANT_URL=os.getenv("QDRANT_URL")
    CRYPTO_COMPARE_API_KEY=os.getenv("CRYPTO_COMPARE_API_KEY")
    llm = AzureOpenAI(
        engine="gpt40",
        temperature=0.0,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=APIKEY_GPT4,
        api_version=API_VERSION
    )
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=API_KEY_QDRANT
    )
    app = AIApplication(
        llm=llm,
        qdrant_client=qdrant_client,
        collection_name=COLLECTION_NAME,
        data_path=DATA_PATH,
        model_name=MODEL_NAME,
        binance_api_key=BINANCE_API_KEY,
        binance_api_secret=BINANCE_API_SECRET
    )
    app.run()
