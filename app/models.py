import os

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain_community.vectorstores.chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
persist_directory = 'app/static/chroma/'
# persist_directory = 'app/docs/chroma'

embedder = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)
gemini = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))
gemini_1 = ChatGoogleGenerativeAI(model="gemini-1.0-pro-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))
mistral = Ollama(model="mistral")
# vectordb = PineconeVectorStore(index_name=os.getenv("INDEX_NAME"), embedding=embedder)
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedder)
retriever = vectordb.as_retriever(kwargs={"k": 5})
