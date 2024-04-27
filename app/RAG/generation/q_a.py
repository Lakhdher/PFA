from operator import itemgetter

from flask_socketio import emit
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda

from app.RAG.generation.history import history_aware_retriever
from app.RAG.utils.prompts import qa_system_prompt
from app.models import gemini

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


async def async_generator_wrapper(sync_gen):
    for item in sync_gen:
        yield item


async def get_response(question, chat_history=[], metadata=None):
    global docs
    response = rag_chain.invoke({"input": question, "chat_history": chat_history})
    return response, docs


async def get_stream_response(question, chat_history=[]):
    answer = []
    metadata = None
    global docs
    async for text in async_generator_wrapper(rag_chain.stream({"input": question, "chat_history": chat_history})):
        if 'answer' in text:
            answer.append(text['answer'].content)
            metadata = text['answer'].response_metadata  # store the metadata
            emit('response', {'data': text['answer'].content, 'metadata': metadata})
    return answer, metadata
