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

class AIApplication:
    def __init__(self, llm, 
                 qdrant_client, 
                 collection_name, 
                 data_path, 
                 model_name):
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
    
        multiply_tool = FunctionTool.from_defaults(fn=self.get_crypt_information, name="cryto_tool")


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

    def get_crypt_information(self):
        """Get information about average price of BNBBTC pair"""

        binance_client = Client(api_key, api_secret)
        avg_price = binance_client.get_avg_price(symbol='BNBBTC')
        # print(avg_price)
        return avg_price

    def run(self):
        self.agent.chat_repl()



if __name__ == "__main__":

    llm = AzureOpenAI(
        engine="gpt40",
        temperature=0.0,
        azure_endpoint=azure_endpoint,
        api_key=api_key_gpt4,
        api_version=api_version
    )
    qdrant_client = QdrantClient(
        url=,
        api_key=api_key_qdrant
    )
    app = AIApplication(
        llm=llm,
        qdrant_client=qdrant_client,
        collection_name=collection_name,
        data_path=data_path,
        model_name=model_name
    )
    app.run()
