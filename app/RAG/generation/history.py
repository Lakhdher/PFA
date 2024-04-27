from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.RAG.retrieval.multiquery import retrieval_chain_multiquery
from app.RAG.utils.prompts import contextualize_q_system_prompt
from app.models import gemini

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    gemini, retrieval_chain_multiquery, contextualize_q_prompt
)
