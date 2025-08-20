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
    st.write(f"Bem-vindo, **{st.session_state['username']}**!")
    st.write(f"Seu nível de acesso é: **{st.session_state['role']}**")
    st.markdown("---")
    st.write("Navegue para as outras páginas no menu à esquerda.")
    if st.button("Logout"):
        fazer_logout()
else:
    # Se não estiver logado, mostre as abas de Login e Cadastro
    st.subheader("Por favor, faça o login ou cadastre-se para continuar")
    
    login_tab, signup_tab = st.tabs(["🔑 Entrar", "✍️ Cadastrar"])

    # Aba de Login
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Usuário", key="login_username")
            password = st.text_input("Senha", type="password", key="login_password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                fazer_login(username, password)

    # Aba de Cadastro
    with signup_tab:
        st.markdown("### Crie sua conta de usuário")
        with st.form("signup_form", clear_on_submit=True):
            new_username = st.text_input("Escolha um nome de usuário")
            new_password = st.text_input("Escolha uma senha", type="password")
            confirm_password = st.text_input("Confirme a senha", type="password")
            
            signup_submitted = st.form_submit_button("Cadastrar")

            if signup_submitted:
                # Validações do formulário de cadastro
                if not (new_username and new_password and confirm_password):
                    st.warning("Por favor, preencha todos los campos.")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem.")
                else:
                    # Tenta adicionar o usuário com o nível "padrão"
                    success = db.adicionar_usuario(new_username, new_password, "padrão")
                    if success:
                        st.success("Conta criada com sucesso!")
                        st.info("Por favor, volte para a aba 'Entrar' para fazer o login.")
                    else:
                        st.error("Este nome de usuário já existe. Por favor, escolha outro.")