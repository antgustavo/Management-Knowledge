import streamlit as st
import os
from dotenv import load_dotenv

# Importações do LangChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain

load_dotenv()

# --- Configuração ---
# Título da página do Streamlit
st.set_page_config(page_title="Consulta ao Grafo com LLM", layout="wide")
st.title("🤖 Assistente de Consulta ao Grafo de Conhecimento")

# --- Interface do Usuário ---
st.markdown("""
**Faça uma pergunta sobre os dados da empresa.**
Exemplos:
- *Quais competências a Ana Carolina Souza possui?*
- *Que pessoas trabalham no projeto 'Sistema de Autenticação Central'?*
- *Liste todos os projetos que utilizam a tecnologia 'Docker'.*
""")

# Campo de input para a pergunta do usuário
user_question = st.text_input("Sua pergunta:", placeholder="Digite aqui...")