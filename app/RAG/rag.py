from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.RAG.utils.prompts import contextualize_q_system_prompt, qa_system_prompt
from app.RAG.retrieval.multiquery import multiquery_retriever

gemini = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", convert_system_message_to_human=True)
mistral = Ollama(model="mistral")
embedder = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)
persist_directory = '../static/chroma/'

vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedder)

retriever = vectordb.as_retriever(k=5)

docs, multiquery_retriever = multiquery_retriever(question="Comment créer un fond de commerce en Tunisie?", retriever=retriever, model=mistral)
print(len(docs))
print(docs[0])
# contextualize_q_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )
#
# history_aware_retriever = create_history_aware_retriever(
#     gemini, multiquery_retriever, contextualize_q_prompt
# )
