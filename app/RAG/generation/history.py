from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.RAG.retrieval.multiquery import retrieval_chain_multiquery
from app.RAG.utils.prompts import contextualize_q_system_prompt
from app.models import gemini,retriever,mistral

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        ("human", contextualize_q_system_prompt),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    mistral, retrieval_chain_multiquery, contextualize_q_prompt
)
