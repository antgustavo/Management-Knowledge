import streamlit as st
import database as db

st.set_page_config(page_title="Administração", page_icon="⚙️", layout="wide")

# --- Verificação de Login e Permissão ---
if not st.session_state.get('logged_in', False):
    st.error("Acesso negado. Por favor, faça o login primeiro.")
    st.stop()
# Verifica se o usuário tem a permissão de administrador
elif st.session_state.get('role') != 'adm':
    st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    st.stop()

# --- Conteúdo da Página de Administração ---
st.title("Painel de Administração")
st.write(f"Bem-vindo, {st.session_state.get('username').capitalize()}!")
st.markdown("---")

# Seção para cadastrar novos usuários
st.subheader("Cadastrar Novo Usuário")

with st.form("signup_form", clear_on_submit=True):
    new_username = st.text_input("Novo Usuário")
    new_password = st.text_input("Nova Senha", type="password")
    new_role = st.selectbox("Nível de Acesso", ["Padrão", "Administrador"])
    signup_submitted = st.form_submit_button("Cadastrar")

    if signup_submitted:
        if new_username and new_password:
            if new_role == "Administrador":
                new_role = "adm"
            if db.adicionar_usuario(new_username, new_password, new_role):
                st.success(f"Usuário '{new_username}' cadastrado com sucesso!")
            else:
                st.error(f"O usuário '{new_username}' já existe.")
        else:
            st.warning("Por favor, preencha todos os campos.")

# Adicione aqui outras funcionalidades de administrador, como modificar dados, etc.
st.subheader("Área para Modificar Dados")
st.write("Aqui você pode adicionar formulários para editar, criar ou deletar dados do seu grafo.")