from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.RAG.utils.prompts import multiquery_and_ragFusion_prompt
from app.RAG.utils.utils import get_unique_union
from app.models import retriever,gemini_1

prompt_perspectives = ChatPromptTemplate.from_template(multiquery_and_ragFusion_prompt)

generate_queries = (
        prompt_perspectives
        | gemini_1
        | StrOutputParser()
        | (lambda x: x.split("\n"))
        | (lambda x: [i for i in x if i])
)
def retrieve(queries):
    return [retriever.invoke(query) for query in queries]

retrieval_chain_multiquery = generate_queries | retrieve | get_unique_union
