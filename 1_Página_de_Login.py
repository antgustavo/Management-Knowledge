import streamlit as st
import database as db

# --- Configuração da Página ---
st.set_page_config(
    page_title="Página de Login",
    page_icon="🔑",
    layout="centered"
)

# --- Inicialização do Banco de Dados ---
# Garante que a tabela de usuários exista ao iniciar o app
db.criar_tabela_usuarios()

# --- Funções Auxiliares (Login/Logout) ---
def fazer_login(username, password):
    """Função para processar o login."""
    user_info = db.verificar_usuario(username, password)
    if user_info:
        st.session_state['logged_in'] = True
        st.session_state['username'] = user_info['username']
        st.session_state['role'] = user_info['role']
        # Limpa as chaves de formulário para evitar reenvio
        st.session_state.pop('login_username', None)
        st.session_state.pop('login_password', None)
        st.rerun() # Recarrega a página para refletir o estado de login
    else:
        st.error("Usuário ou senha inválidos.")

def fazer_logout():
    """Função para processar o logout."""
    st.session_state['logged_in'] = False
    st.session_state.pop('username', None)
    st.session_state.pop('role', None)
    st.rerun()

# --- Lógica da Interface ---

st.title("Sistema de Autenticação e Consulta")

# Se o usuário já estiver logado, mostre a mensagem de boas-vindas e o botão de logout
if st.session_state.get('logged_in', False):
    st.sidebar.success(f"Logado como {st.session_state['username']}")
    st.write(f"Bem-vindo, **{st.session_state['username'].capitalize()}**!")
    st.write(f"Seu nível de acesso é: **{st.session_state['role']}**")
    st.markdown("---")
    st.write("Navegue para as outras páginas no menu à esquerda.")
    if st.button("Logout"):
        fazer_logout()
else:
    # Se não estiver logado, mostre as abas de Login e Cadastro
    st.subheader("Por favor, faça o login para continuar")
    
    with st.form("login_form"):
        username = st.text_input("Usuário", key="login_username")
        password = st.text_input("Senha", type="password", key="login_password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            fazer_login(username, password)