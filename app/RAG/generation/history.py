from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.models import gemini
from app.RAG.retrieval.multiquery import multiquery

contextualize_q_system_prompt = """ Compte tenu de l'historique des discussions et de la dernière question de l'utilisateur \
qui peut faire référence à un contexte dans l'historique de la discussion, formuler quelques phrase autonome \
qui peut récapituler l'historique de la discussion. Prenez en compte que vous êtes toujours en Tunisie.\
Ne PAS répondre à la question,juste la reformuler si nécessaire et sinon la renvoyer telle quelle."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    gemini, multiquery(), contextualize_q_prompt
)
