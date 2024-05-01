from operator import itemgetter

from flask_socketio import emit
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_mongodb import MongoDBChatMessageHistory
from langchain_mongodb.cache import MongoDBAtlasSemanticCache
from langchain_core.globals import set_llm_cache

from app.RAG.generation.history import history_aware_retriever
from app.RAG.utils.prompts import qa_system_prompt
from app.RAG.utils.utils import async_generator_wrapper
from app.config.mongoConfig import get_mongo_uri, get_db_name, get_collection_name
from app.models import gemini

import time

db_uri = get_mongo_uri()
db_name = get_db_name()
collection_name = get_collection_name()



qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("assistant", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
docs = []


def save_docs(inputs):
    global docs
    docs = [x.metadata for x in inputs['context']]
    return inputs['context']


question_answer_chain = (
        RunnableParallel({
            'context': RunnableLambda(save_docs),
            'chat_history': itemgetter('chat_history'),
            'input': itemgetter('input')})
        | qa_prompt
        | gemini

)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(db_uri, session_id, database_name=db_name, collection_name=collection_name, )


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


async def get_response(question, session_id):
    global docs
    global store
    response = conversational_rag_chain.invoke({"input": question},
                                               config={
                                                   "configurable": {"session_id": session_id, }
                                               })
    return response, docs


async def get_stream_response(question, session_id):
    answer = []
    metadata = None
    global docs
    global store
    start_time = time.time()
    async for text in async_generator_wrapper(
            conversational_rag_chain.stream({"input": question}, config={"configurable": {"session_id": session_id}})):
        if 'answer' in text:
            end_time = time.time()
            print('Time taken for response:', end_time - start_time)
            answer.append(text['answer'].content)
            metadata = text['answer'].response_metadata  # store the metadata
            emit('response', {'data': text['answer'].content, 'metadata': metadata})
    emit('response', {'data': '\n\n', 'metadata': metadata})        
    return answer, metadata
