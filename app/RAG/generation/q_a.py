from operator import itemgetter
from flask_socketio import emit
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda
from app.RAG.generation.history import history_aware_retriever
from app.models import gemini

docs = []

qa_system_prompt = """ Tu es un assistant juridique spécialisé dans la loi en TUNISIE.
    Ta mission est de répondre aux questions des gens sur différents aspects juridiques ,en te limitant aux informations générales et en évitant les cas sensibles ou extrêmes.
    Si une question dépasse ton champ d'expertise ou si elle concerne un sujet très délicat, tu dois informer l'utilisateur que tu ne peux pas fournir d'aide spécifique dans ce cas.
    Utilise les pièces suivantes du contexte pour répondre. Utilise un langage simple et accessible pour garantir que tout le monde puisse comprendre tes réponses.
    developper autant que possible et donner des exemples si necessaire.
    Contexte: {context}.Cite à la fin les articles du contexte."""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("assistant", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


def save_docs(inputs):
    global docs
    docs = [x.metadata for x in inputs['context']]
    print(inputs)
    return docs


question_answer_chain = (
        RunnableParallel({
            'context': RunnableLambda(save_docs),
            'chat_history': itemgetter('chat_history'),
            'input': itemgetter('input')})
        | qa_prompt
        | gemini

)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


async def async_generator_wrapper(sync_gen):
    for item in sync_gen:
        yield item


async def get_response(question, chat_history=[], metadata=None):
    answer = []
    global docs
    async for text in async_generator_wrapper(rag_chain.stream({"input": question, "chat_history": chat_history})):
        if 'answer' in text:
            answer.append(text['answer'].content)
            metadata = text['answer'].response_metadata  # store the metadata
    return answer, metadata, docs


async def get_stream_response(question, chat_history=[]):
    answer = []
    metadata = None
    global docs
    async for text in async_generator_wrapper(rag_chain.stream({"input": question, "chat_history": chat_history})):
        if 'answer' in text:
            answer.append(text['answer'].content)
            print(text['answer'].content, flush=True)
            metadata = text['answer'].response_metadata
            emit('stream_qa', {'data': text['answer'].content})
    return answer, metadata, docs
