from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain # Cadeia específica para Q&A com Cypher
from langchain.prompts import PromptTemplate
import streamlit as st

# --- Conexao com o Neo4j
@st.cache_resource
def ConnectToGraph(uri, username, password):
    try:
        graph = Neo4jGraph(
            url=uri,
            username=username,
            password=password
        )

    except Exception as e:
        print(f"Erro ao conectar-se ao Neo4j: {e}")
        graph = None
        exit()

    return graph

# --- Criacao da cadeia ---

def CreateChain(graph, llm, CYPHER_GENERATION_PROMPT, QA_PROMPT):
    """
    Cria uma cadeia de perguntas e respostas usando Cypher para o grafo Neo4j.
    """
    cypher_chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        prompt=CYPHER_GENERATION_PROMPT,
        qa_prompt=QA_PROMPT,
        allow_dangerous_requests=True,
        validate_cypher=True,
    )
    return cypher_chain

# --- Definicao do modelo de LLM ---

def CreateLLM(model, openai_api_key):
    """
    Cria um modelo de linguagem usando OpenAI.
    """
    llm = ChatOpenAI(model=model, temperature=0, api_key=openai_api_key)

    CYPHER_GENERATION_TEMPLATE = """
    Você é um expert em Neo4j e Cypher. Dada uma pergunta em linguagem natural e um esquema de grafo,
    gere uma query Cypher para responder à pergunta. NÃO RESPONDA A PERGUNTA, apenas gere a query.
    Não use exemplos na query, apenas o que for necessário com base na pergunta e no esquema.
    Não coloque a query dentro de blocos de código markdown. Retorne apenas a query Cypher.

    Esquema do Grafo:
    {schema}

    Pergunta: {query}
    Query Cypher:
    """
    CYPHER_GENERATION_PROMPT = PromptTemplate(
        input_variables=["schema", "query"], template=CYPHER_GENERATION_TEMPLATE
    )

    # Este é o prompt para gerar a resposta final com base nos resultados da query
    QA_TEMPLATE = """Você é um assistente de IA que resume resultados de uma consulta a um banco de dados de grafo para responder a uma pergunta.
    Use os dados fornecidos no contexto para formular uma resposta clara e em linguagem natural.
    O contexto abaixo está em formato de lista de dicionários (JSON), que é o resultado da consulta.

    **Instruções Importantes:**
    1.  Sintetize os resultados em uma resposta útil e direta.
    2.  Se a lista no contexto contiver dados, extraia a informação e responda à pergunta.
    3.  Se a lista no contexto estiver vazia (`[]`), isso significa que nenhuma informação foi encontrada. Nesse caso, e somente nesse caso, diga: "Não encontrei informações sobre isso no banco de dados."
    4.  Combine os resultados de forma natural. Por exemplo, se o resultado for `[{"nome": "Ana"}, {"nome": "Bruno"}]`, responda "As pessoas encontradas foram Ana e Bruno." e não o JSON cru.

    Contexto:
    {context}

    Pergunta: {query}
    Resposta útil:"""
    QA_PROMPT = PromptTemplate(input_variables=["context", "query"], template=QA_TEMPLATE)
    
    return llm, CYPHER_GENERATION_PROMPT, QA_PROMPT