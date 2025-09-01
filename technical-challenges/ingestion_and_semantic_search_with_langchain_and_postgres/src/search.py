import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.runnables import chain
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


@chain
def search_prompt(input_dict: dict):
    question = input_dict["question"]
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL"))
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )
    results = store.similarity_search_with_score(question, k=10)

    context = ""
    for document, score in results:
        context += document.page_content.strip() + "\n"

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE, input_variables=["contexto", "pergunta"]
    )
    full_prompt = prompt.format(contexto=context, pergunta=question)

    return full_prompt


if __name__ == "__main__":
    question = "Qual é o faturamento da Gamma IA LTDA?"
    chain = search_prompt
    print(chain.invoke({"question": question}))
