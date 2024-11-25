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
from fastapi.responses import StreamingResponse
# from llama_index.agent.openai import ReActAgent, OpenAIAgent
from llama_index.core.agent import AgentRunner, ReActAgentWorker, ReActAgent, ReActChatFormatter

SYSTEM_PROMPT="""
You have to answer the questions with funny style. 
"""

# SYSTEM_HEADER="""

# System Prompt

# You are designed to help with a variety of tasks, ranging from answering questions to providing summaries and performing other types of analyses.

# ---

# Tools

# You have access to a wide variety of tools. You are responsible for using these tools in any sequence you deem appropriate to complete the task at hand.
# This may require breaking the task into subtasks and using different tools to complete each subtask.

# You have access to the following tools:
# {tool_desc}

# ---

# Output Format

# Please answer in the same language as the question and follow the format below:

# 1. When deciding to use a tool:

# Thought: The current language of the user is: (user's language). I need to use a tool to help me answer the question.
# Action: [tool name (one of {tool_names})]
# Action Input: { valid JSON input for the tool, e.g., {"input": "hello world", "num_beams": 5} }

# 2. When the tool responds, the user will provide feedback in the following format:

# Observation: [tool response]

# 3. If additional tools or clarifications are needed, repeat the format. Continue this loop until you have enough information to answer the question.

# ---

# Final Response

# When you have enough information to answer without using any more tools, you MUST respond in one of the following formats:

# 1. If you can answer the question:

# Thought: I can answer without using any more tools. I'll use the user's language to answer.
# Answer: [your answer here (in the same language as the user's question)]

# 2. If you cannot answer the question:

# Thought: I cannot answer the question with the provided tools.
# Answer: [your explanation here (in the same language as the user's question)]

# ---

# Guidelines

# 1. Always start with a Thought. Clearly identify the user's language and whether a tool is needed to proceed.
# 2. Use Valid JSON Format: Ensure the Action Input is in valid JSON. For example:
#    - Correct: {"input": "hello world", "num_beams": 5}
#    - Incorrect: {{'input': 'hello world', 'num_beams': 5}}
# 3. Clarity in Response: Never surround your response with unnecessary code markers like markdown blocks. Use only where necessary within your response.

# ---

# Current Conversation

# Below is the current conversation consisting of interleaving human and assistant messages.

# """

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
        # custom_formatter = ReActChatFormatter(context=SYSTEM_PROMPT)
        # custom_formatter = ReActChatFormatter(system_header=SYSTEM_HEADER)
        # self.agent = ReActAgentWorker.from_tools(all_tools, llm=self.llm, verbose=True, react_chat_formatter=custom_formatter)
        # self.agent = ReActAgentWorker.from_tools(all_tools, llm=self.llm, verbose=True)
        # self.agent = OpenAIAgent.from_tools(all_tools, llm=self.llm, verbose=True, system_prompt=system_prompt)
        self.agent = ReActAgent.from_tools(all_tools, llm=self.llm, verbose=True)

        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret

    async def chat(self, message: str):
        # Async method to interact with OpenAIAgent
        print(message)
        response = await self.agent.achat(message)  # Assuming 'achat' is the async method
        return str(response)


    async def stream_chat(self, message: str):
        response = await self.agent.astream_chat(message)  # Assuming 'astream_chat' is the async method
        response_text = ""
        async for token in response.async_response_gen():  # Stream tokens as they arrive
            response_text += token  # Append each token to the response text
            yield token  # Yield each token as it arrives (this could be printed or processed)
        # return response_text  # Optionally return the complete response after streaming

    # async def stream_chat(self, message: str):
    #     response = await self.agent.astream_chat(message)
    #     response_gen = response.response_gen  # Extract the response generator
    #     async response_text = ""
    #     async for token in response.async_response_gen():
    #         response_text += token  # Append each token to the response text
    #         yield token  # Yield each token as it arrives (this could be printed or processed)
    #     return response_text  # Optionally return the complete response after streaming

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

@app.post("/ask_stream")
async def ask_query(query_request: QueryRequest):
    query = query_request.query
    try:
        response = ai_app.stream_chat(query)  # Call the chat method (async)
        return StreamingResponse(response, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask_query(query_request: QueryRequest):
    query = query_request.query
    try:
        response = await ai_app.chat(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
