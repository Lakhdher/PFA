from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.RAG.utils.prompts import multiquery_and_ragFusion_prompt
from app.RAG.utils.utils import get_unique_union
from app.models import retriever, mistral,gemini_1

prompt_perspectives = ChatPromptTemplate.from_template(multiquery_and_ragFusion_prompt)

generate_queries = (
        prompt_perspectives
        | gemini_1
        | StrOutputParser()
        | (lambda x: x.split("\n"))
        | (lambda x: [i for i in x if i])
)

retrieval_chain_multiquery = generate_queries | retriever.map() | get_unique_union
