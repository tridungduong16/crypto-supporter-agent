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
from src.agents.tools import create_query_engine_tools
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class AIApplication:
    def __init__(self, llm, 
                 qdrant_client, 
                 collection_name, 
                 data_path, 
                 model_name, 
                 binance_api_key, 
                 binance_api_secret,
                 news_api_key, reddit_client_id, reddit_client_secret,
                 system_prompt):
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
        self.binance_api_key, self.binance_api_secret = binance_api_key, binance_api_secret
        all_tools = create_query_engine_tools(self.binance_api_key, self.binance_api_secret, news_api_key, reddit_client_id, reddit_client_secret)
        self.agent = OpenAIAgent.from_tools(all_tools, llm=self.llm, verbose=True, system_prompt=system_prompt)
        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret

    def run(self):
        # Async method to interact with OpenAIAgent
        self.agent.chat_repl()


# FastAPI Integration
app = FastAPI()

# Pydantic model to accept input
class QueryRequest(BaseModel):
    query: str

# Initialize the AIApplication with required parameters
llm = AzureOpenAI(
    engine="gpt40",
    temperature=0.0,
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key=os.getenv("APIKEY_GPT4"),
    api_version=os.getenv("API_VERSION")
)

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("API_KEY_QDRANT")
)

# Initialize the app instance
ai_app = AIApplication(
    llm=llm,
    qdrant_client=qdrant_client,
    collection_name=os.getenv("COLLECTION_NAME"),
    data_path=os.getenv("DATA_PATH"),
    model_name=os.getenv("MODEL_NAME"),
    binance_api_key=os.getenv("BINANCE_API_KEY"),
    binance_api_secret=os.getenv("BINANCE_API_SECRET"),
    news_api_key=os.getenv("news_api_key"), 
    reddit_client_id=os.getenv("reddit_client_id"), 
    reddit_client_secret=os.getenv("reddit_client_secret"),
    system_prompt=os.getenv("SYSTEM_PROMPT")
)

ai_app.run()
# @app.post("/ask")
# async def ask_query(query_request: QueryRequest):
#     query = query_request.query
#     try:
#         response = await ai_app.chat(query)
#         return {"response": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # Entry point for testing purposes
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
