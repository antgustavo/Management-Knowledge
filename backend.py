import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain # Cadeia específica para Q&A com Cypher
from langchain.prompts import PromptTemplate

# --- Carrega as variaveis de ambiente

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = ""


# --- Conexao com o Neo4j

try:
    graph = Neo4jGraph(
        url= uri,
        username = username,
        password=password
    )

except Exception as e:
    print("Erro ao conectar-se ao Neo4j: {e}")
    graph = None
    exit()

# --- Definicao do modelo de LLM ---

llm = ChatOpenAI(model=model, temperature=0, api_key=openai_api_key)

# --- Criacao da cadeia ---

chain = GraphCypherQAChain(
    graph=graph,
    llm=llm,
    verbose=True
)