import streamlit as st
from backend import *

st.set_page_config(page_title="Consulta", page_icon="👤", layout="wide")

# --- Verificação de Login ---
# A primeira coisa a fazer em cada página protegida é verificar o login
if not st.session_state.get('logged_in', False):
    st.error("Acesso negado. Por favor, faça o login primeiro.")
    st.stop() # Interrompe a execução da página

# --- Conteúdo da Página ---
st.title("Página de Consulta de Dados")
st.write(f"Bem-vindo, {st.session_state.get('username', 'Usuário').capitalize()}!")
st.markdown("---")
st.write("Esta é a área onde usuários padrão podem apenas visualizar informações.")

# Exemplo de conteúdo de consulta
st.markdown("""
**Faça uma pergunta sobre os dados da empresa.**
Exemplos:
- *Quais competências a Ana Carolina Souza possui?*
- *Que pessoas trabalham no projeto 'Sistema de Autenticação Central'?*
- *Liste todos os projetos que utilizam a tecnologia 'Docker'.*
""")

# Campo de input para a pergunta do usuário
user_question = st.text_input("Sua pergunta:", placeholder="Digite aqui...")
