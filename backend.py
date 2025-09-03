from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# --- Carrega as variaveis de ambiente

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-5-mini"

# --- Conexao com o Neo4j

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
        cypher_prompt=CYPHER_GENERATION_PROMPT,
        qa_prompt=QA_PROMPT,
        allow_dangerous_requests=True,
        validate_cypher=True,
        return_intermediate_steps = True
    )
    return cypher_chain

# --- Definicao do modelo de LLM ---

def CreateLLM(model, openai_api_key):
    """
    Cria um modelo de linguagem usando OpenAI.
    """
    llm = ChatOpenAI(model=model, temperature=0.2, api_key=openai_api_key)

    CYPHER_GENERATION_TEMPLATE = """
    Você é um expert em Neo4j e Cypher. Dada uma pergunta em linguagem natural e um esquema de grafo,
    gere uma query Cypher para responder à pergunta. NÃO RESPONDA A PERGUNTA, apenas gere a query.
    Não use exemplos na query, apenas o que for necessário com base na pergunta e no esquema.
    Não coloque a query dentro de blocos de código markdown. Retorne apenas a query Cypher.
    
    Se a pergunta contiver termos que não batem exatamente com os valores armazenados no grafo,
    gere uma query Cypher que use buscas parciais ou flexíveis:
    
    - Sempre normalize comparações de texto com `toLower()`.
    - Entenda palavra militares como pessoas, não como cargo ou patente.
    - Entenda sinônimo de pessoas, por exemplo: 'Quais militares' ou 'Quais servidores/contribuidores' pode querer dizer 'Quais pessoas'.
    - Se possível, use `CONTAINS` ou `IN` para capturar sinônimos e variações.
    - Nunca use igualdade exata em strings de status ou categorias.
    - Quando comparar datas, sempre converta strings para date()/datetime().
     Exemplo: Para `após 2022`, use date(prop) > date('2022-12-31') (ou >= date('2023-01-01')).
    - Nunca compare datas como strings simples (ex.: '2022').
    - Se houver sinônimos possíveis (ex: 'conf' e 'conferência', 'artigo' e 'publicacao/publicação'), considere ambos.
    - Considere erros de grafia e acentuações.
    - Atente-se para SIGLAS (ex: USP é o mesmo que Universidade de São Paulo, ITA e Instituto Tecnológico de Aeronáutica).
    - Evite depender de igualdade exata para strings.


    Esquema do Grafo:
    {schema}

    Pergunta: {question}
    Query Cypher:
    """
    CYPHER_GENERATION_PROMPT = PromptTemplate(
        input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
    )

    # Este é o prompt para gerar a resposta final com base nos resultados da query
    QA_TEMPLATE = """Você é um assistente de IA que resume resultados de uma consulta a um banco de dados de grafo para responder a uma pergunta.
    Use os dados fornecidos no contexto para formular uma resposta clara e em linguagem natural.
    O contexto abaixo está em formato de lista de dicionários (JSON), que é o resultado da consulta.

    **Instruções Importantes:**
    1.  Se a lista no contexto estiver vazia (`[]`), responda exatamente: 'Não encontrei informações sobre isso no banco de dados.'
    2.  Caso contrário, leia as chaves e valores retornados no JSON e use-os para montar uma resposta em português claro.
    3.  Se houver múltiplos resultados, combine-os de forma natural, sem repetir estrutura JSON. 
    4.  Exemplo: se o contexto for
       `[{{"Projeto": "Sistema X", "Responsavel": "Maria Silva"}}, {{"Projeto": "Sistema Y", "Responsavel": "João Souza"}}]`
       você deve responder algo como:
       "Os projetos Sistema X (responsável: Maria Silva) e Sistema Y (responsável: João Souza) possuem documentação publicada após 2022."

    Contexto:
    {context}

    Pergunta: {question}
    Resposta útil:"""


    QA_PROMPT = PromptTemplate(input_variables=["context", "question"], template=QA_TEMPLATE)
    
    return llm, CYPHER_GENERATION_PROMPT, QA_PROMPT