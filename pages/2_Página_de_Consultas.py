import streamlit as st
from backend import chain

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

if user_question:
    # Mostra um spinner de carregamento enquanto a consulta está sendo processada
    with st.spinner("Buscando a resposta no grafo de conhecimento..."):
        try:
            # 1. CHAMA A CADEIA DO BACK-END: 
            #    Envia a pergunta do usuário para a chain do LangChain.
            response = chain.invoke({"query": user_question})

            # 2. EXIBE A RESPOSTA FINAL:
            #    O dicionário de resposta contém a chave "result" com a resposta em linguagem natural.
            st.subheader("Resposta:")
            st.markdown(response["result"])

            # 3. (Opcional, mas muito útil) MOSTRA A CONSULTA CYPHER GERADA:
            #    Isso é ótimo para depuração e para entender como a LLM está pensando.
            with st.expander("Ver detalhes da execução"):
                st.write("**Consulta Cypher Gerada:**")
                # A consulta fica aninhada dentro de 'intermediate_steps'
                if response.get("intermediate_steps") and len(response["intermediate_steps"]) > 0:
                    cypher_query = response["intermediate_steps"][0].get("query", "Não foi possível extrair a consulta.")
                    st.code(cypher_query, language="cypher")
                else:
                    st.write("Nenhuma consulta Cypher foi gerada ou encontrada.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")