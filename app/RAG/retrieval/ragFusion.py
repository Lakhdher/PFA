from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.RAG.utils.prompts import multiquery_and_ragFusion_prompt
from app.RAG.utils.utils import reciprocal_rank_fusion
from app.models import retriever, mistral,gemini_1

prompt_perspectives = ChatPromptTemplate.from_template(multiquery_and_ragFusion_prompt)

generate_queries = (
        prompt_perspectives
        | gemini_1
        | StrOutputParser()
        | (lambda x: x.split("\n"))
)

retrieval_chain_rag_fusion = generate_queries | retriever.map() | reciprocal_rank_fusion
