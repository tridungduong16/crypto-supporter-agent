import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import pdb

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


class QdrantHandler:
    def __init__(self):
        """Initialize QdrantHandler with Qdrant client and embedding model."""
        load_dotenv()

        # Load environment variables
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("API_KEY_QDRANT")
        self.collection_name = os.getenv("COLLECTION_NAME", "default_collection")
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.dimensions = 384  # Default dimension size for embeddings

        # Initialize embeddings, Qdrant client, and vector store
        self.embeddings = self._initialize_embeddings()
        self.qdrant_client = self._initialize_qdrant_client()
        # self._initialize_collection()
        self.vector_store = self._initialize_vector_store()

    def _initialize_embeddings(self):
        """Initialize HuggingFace embeddings."""
        model_kwargs = {"device": "cpu", "trust_remote_code": True}
        return HuggingFaceEmbeddings(
            model_name=self.embedding_model_name, model_kwargs=model_kwargs
        )

    def _initialize_qdrant_client(self):
        """Initialize Qdrant client."""
        return QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )

    def _initialize_collection(self):
        """Ensure the Qdrant collection exists."""
        # self.qdrant_client.delete_collection(collection_name=self.collection_name)
        try:
            collection_info = self.qdrant_client.get_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            if "Not found" in str(e):
                print(f"Collection '{self.collection_name}' not found. Creating it now...")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.dimensions, distance=Distance.COSINE)
                )
                print(f"Collection '{self.collection_name}' created.")
            else:
                print(f"Error initializing collection: {str(e)}")
                raise

    def _initialize_vector_store(self):
        """Initialize Qdrant vector store."""
        return QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    def index_documents(self, documents):
        """Index provided documents into Qdrant."""
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)
        print("Documents indexed successfully.")

    def retrieve(self, query, k=2):
        """Retrieve documents from Qdrant."""
        results = self.vector_store.similarity_search(query, k=k)
        for res in results:
            print(f"* {res.page_content} [{res.metadata}]")
        return results

    def extract_text_from_txt(self, folder_path):
        """Extract text from all TXT files in a folder."""
        txt_texts = []
        try:
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, "r", encoding="utf-8") as file:
                        text = file.read()
                        txt_texts.append((file_name, text.strip()))
                        print(f"Extracted text from {file_name}.")
        except Exception as e:
            print(f"Error reading TXT files: {str(e)}")
            raise
        return txt_texts

    def extract_text_from_pdfs(self, folder_path):
        """Extract text from all PDF files in a folder."""
        pdf_texts = []
        try:
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".pdf"):
                    file_path = os.path.join(folder_path, file_name)
                    pdf_text = self._extract_text_from_pdf(file_path)
                    pdf_texts.append((file_name, pdf_text))
                    print(f"Extracted text from {file_name}.")
        except Exception as e:
            print(f"Error reading PDFs: {str(e)}")
            raise
        return pdf_texts

    def _extract_text_from_pdf(self, file_path):
        """Extract text from a single PDF file."""
        try:
            reader = PdfReader(file_path)
            text = "".join(page.extract_text() for page in reader.pages)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return ""


# Document Data
DOCUMENTS = [
    Document(page_content="Duong Tri Dung\nPhone number: (+61) 411948899", metadata={"source": "tweet"}),
    Document(page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.", metadata={"source": "news"}),
    Document(page_content="Building an exciting new project with LangChain - come check it out!", metadata={"source": "tweet"}),
    Document(page_content="Robbers broke into the city bank and stole $1 million in cash.", metadata={"source": "news"}),
    Document(page_content="Wow! That was an amazing movie. I can't wait to see it again.", metadata={"source": "tweet"}),
    Document(page_content="Is the new iPhone worth the price? Read this review to find out.", metadata={"source": "website"}),
    Document(page_content="The top 10 soccer players in the world right now.", metadata={"source": "website"}),
    Document(page_content="LangGraph is the best framework for building stateful, agentic applications!", metadata={"source": "tweet"}),
    Document(page_content="The stock market is down 500 points today due to fears of a recession.", metadata={"source": "news"}),
    Document(page_content="I have a bad feeling I am going to get deleted :(", metadata={"source": "tweet"}),
]

if __name__ == "__main__":
    handler = QdrantHandler()
    # handler.index_documents(DOCUMENTS)
    handler.retrieve("Duong Tri Dung")
