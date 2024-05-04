from operator import itemgetter
import time

from flask_socketio import emit
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_mongodb import MongoDBChatMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec

from app.RAG.generation.history import history_aware_retriever
from app.RAG.utils.prompts import qa_system_prompt
from app.RAG.utils.utils import async_generator_wrapper
from app.RAG.utils.parser import streaming_parser
from app.config.mongoConfig import get_mongo_uri, get_db_name, get_collection_name
from app.models import gemini

db_uri = get_mongo_uri()
db_name = get_db_name()
collection_name = get_collection_name()
docs = []
metadata = None


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
    return inputs['context']


async def parser(input):
    global metadata
    metadata = input.response_metadata
    return input.content

question_answer_chain = (
        RunnableParallel({
            'context': RunnableLambda(save_docs),
            'chat_history': itemgetter('chat_history'),
            'input': itemgetter('input')})
        | qa_prompt
        | gemini
        | streaming_parser
        )

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


def get_session_history(user_id: str,conversation_id:str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(db_uri, [user_id,conversation_id], database_name=db_name, collection_name=collection_name, )


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
     history_factory_config=[
        ConfigurableFieldSpec(
            id="user_id",
            annotation=str,
            name="User ID",
            description="Unique identifier for the user.",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="conversation_id",
            annotation=str,
            name="Conversation ID",
            description="Unique identifier for the conversation.",
            default="",
            is_shared=True,
        ),
    ],
)


async def get_response(question, user_id, conversation_id):
    global docs
    response = conversational_rag_chain.invoke({"input": question},
                                               config={
                                                   "configurable": {"user_id": user_id, "conversation_id": conversation_id}
                                               })
    return response, docs


async def get_stream_response(question, user_id, conversation_id):
    answer = []
    global metadata 
    global docs
    async for text in async_generator_wrapper(conversational_rag_chain.stream({"input": question}, config={"configurable": {"user_id": user_id, "conversation_id": conversation_id}})):
        if 'answer' in text:
            answer.append(text['answer'])
            emit('response', {'data': text['answer'], 'metadata': metadata})
    emit('response', {'data': '\n\n', 'metadata': metadata})        
    return answer, metadata
