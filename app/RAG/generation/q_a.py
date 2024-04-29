from operator import itemgetter

from flask_socketio import emit
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.RAG.generation.history import history_aware_retriever
from app.RAG.utils.prompts import qa_system_prompt
from app.RAG.utils.utils import chat_message_history_to_json, json_to_chat_message_history, async_generator_wrapper
from app.config.mongoConfig import get_db
from app.models import gemini

db_client = get_db()
chat_history_collection = db_client['chat_history']

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
    return docs


# uncomment this chain to get safety ratings with the answer


question_answer_chain = (
        RunnableParallel({
            'context': RunnableLambda(save_docs),
            'chat_history': itemgetter('chat_history'),
            'input': itemgetter('input')})
        | qa_prompt
        | gemini

)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

store = {}


def get_session_history(session_id: str):
    if chat_history_collection.count_documents({'session_id': session_id}) == 0:
        store[session_id] = ChatMessageHistory()
        chat_history_collection.insert_one(
            {'session_id': session_id, 'history': chat_message_history_to_json(store[session_id])})
    chat_history = chat_history_collection.find_one({'session_id': session_id})
    store[session_id] = json_to_chat_message_history(chat_history['history'])
    return store[session_id]


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
    list_to_persist = chat_message_history_to_json(store[session_id])
    chat_history_collection.update_one({'session_id': session_id}, {'$set': {'history': list_to_persist}})
    return response, docs


async def get_stream_response(question, session_id):
    answer = []
    metadata = None
    global docs
    global store
    async for text in async_generator_wrapper(
            conversational_rag_chain.stream({"input": question}, config={"configurable": {"session_id": session_id}})):
        if 'answer' in text:
            answer.append(text['answer'].content)
            metadata = text['answer'].response_metadata  # store the metadata
            emit('response', {'data': text['answer'].content, 'metadata': metadata})
    list_to_persist = chat_message_history_to_json(store[session_id])
    chat_history_collection.update_one({'session_id': session_id}, {'$set': {'history': list_to_persist}})
    return answer, metadata
