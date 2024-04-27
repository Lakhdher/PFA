from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.RAG.utils.prompts import multiquery_and_ragFusion_prompt
from app.RAG.utils.utils import get_unique_union
from app.models import retriever, mistral

prompt_perspectives = ChatPromptTemplate.from_template(multiquery_and_ragFusion_prompt)

generate_queries = (
        prompt_perspectives
        | mistral
        | StrOutputParser()
        | (lambda x: x.split("\n"))
)

retrieval_chain_multiquery = generate_queries | retriever.map() | get_unique_union
