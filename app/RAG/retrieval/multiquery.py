from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.RAG.utils.utils import get_unique_union


def multiquery(question, retriever, model):
    template = """Tu es un assistant juridique. 
    Votre mission consiste à générer cinq versions différentes de la question initiale de l'utilisateur,
    afin de récupérer des documents pertinents dans une base de données vectorielle. 
    En proposant plusieurs points de vue sur la question de l'utilisateur, votre objectif
    est de l'aider à surmonter certaines limitations de la recherche de similarité basée sur la distance. 
    Fournissez ces questions alternatives séparées par des sauts de ligne. Question originale: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    generate_queries = (
            prompt_perspectives
            | model
            | StrOutputParser()
            | (lambda x: x.split("\n"))
    )

    retrieval_chain = generate_queries | retriever.map() | get_unique_union
    docs = retrieval_chain.invoke({"question": question})
    return docs, retrieval_chain