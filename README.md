# 🧠 Management Knowledge

## 📘 Visão Geral
O **Management Knowledge** é um sistema desenvolvido em **Python** com **Streamlit**, voltado para **gestão e consulta de conhecimento organizacional**.  
Ele oferece uma **interface web interativa** para login, administração de usuários e consultas, além de um **backend integrado** que gerencia autenticação, persistência de dados e controle de acesso.

O foco do projeto é fornecer uma base sólida para aplicações que precisem de:
- Controle de usuários (autenticação e níveis de permissão)
- Armazenamento local leve (SQLite)
- Interface moderna e acessível via navegador
- Backend centralizado para gerenciar as operações

---

## 🏗️ Estrutura do Projeto

```
Management-Knowledge/
│
├── backend.py                 # Núcleo do backend: lógica do sistema e comunicação com o banco
├── create_adm.py              # Script para criar um usuário administrador
├── database.py                # Módulo de interface com o banco SQLite (CRUD)
├── users.db                   # Banco de dados local SQLite (gerado automaticamente)
│
├── pages/
│   ├── 1_Página_de_Login.py           # Página inicial (autenticação)
│   ├── 2_Página_de_Consultas.py       # Página de consultas e visualização de dados
│   └── 3_Página_do_Administrador.py   # Página de administração (criação/remoção de usuários)
│
├── requirements.txt            # Dependências do projeto
└── README.md
```

---

## ⚙️ Tecnologias Utilizadas
- **Python 3.10+**
- **Streamlit** — construção das interfaces web  
- **SQLite3** — banco de dados leve e local  
- **Pandas / JSON** — manipulação de dados nas páginas  
- **Hashlib / bcrypt** — hashing de senhas  
- **OS / Pathlib** — manipulação de arquivos locais  

---

## 🚀 Instalação e Execução

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/antgustavo/Management-Knowledge.git
cd Management-Knowledge
```

### 2️⃣ Criar e ativar um ambiente virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3️⃣ Instalar as dependências
```bash
pip install -r requirements.txt
```

---

## 🧩 Estrutura Lógica do Sistema
O projeto segue uma separação simples, mas eficiente, entre **backend**, **banco de dados** e **interface (pages)**.

---

### 🧠 1. `database.py` — Camada de Dados (Banco de Dados)
Responsável por toda a comunicação com o banco **SQLite (`users.db`)**.  
Contém as funções CRUD (Create, Read, Update, Delete) relacionadas à tabela de usuários.

#### Funções típicas:
- `create_table()` → Cria a tabela `users` se ainda não existir  
- `add_user(username, password, is_admin)` → Insere um novo usuário com senha criptografada  
- `get_user(username)` → Retorna informações do usuário (para login)  
- `list_users()` → Retorna todos os usuários cadastrados  
- `delete_user(username)` → Remove um usuário específico  

> 💡 **Observação:**  
> O banco `users.db` é criado automaticamente na primeira execução.  
> Não é necessário criá-lo manualmente.

---

### 🔐 2. `create_adm.py` — Criação do Usuário Administrador
Script usado para **inicializar o banco com um administrador**.  
Ele utiliza as funções do `database.py` para garantir que o admin seja criado corretamente.

#### Execução:
```bash
python create_adm.py
```

Durante a execução, o script:
- Cria a tabela de usuários (caso não exista);
- Solicita login e senha do administrador (ou usa valores padrão definidos no código);
- Armazena o admin com a flag `is_admin=True`.

> 💡 **Dica:**  
> Execute este script **apenas uma vez**, logo após instalar o projeto.  
> Caso já exista um administrador, o script ignora a criação.

---

### ⚙️ 3. `backend.py` — Lógica Central
O **núcleo do sistema**, que atua como intermediário entre as páginas do Streamlit e o banco de dados.  
Gerencia autenticação, criptografia, controle de sessão e permissões.

#### Principais responsabilidades:
- Autenticação de usuários  
- Criptografia e validação de senhas  
- Controle de sessão e permissões  
- Funções auxiliares para as páginas (`logout`, `checagem de admin`, etc.)

#### Funções comuns:
- `login_user(username, password)`  
- `register_user(username, password)`  
- `check_admin(username)`  
- `logout_user()`

Essas funções são chamadas diretamente pelas páginas dentro do diretório `pages/`.

---

### 🖥️ 4. `pages/` — Interface Web com Streamlit
O **Streamlit** organiza a interface em páginas (arquivos `.py` dentro da pasta `pages/`).  
Cada página é exibida como uma **aba acessível pelo menu lateral**.

#### 📄 `1_Página_de_Login.py`
- Primeira página exibida ao abrir o sistema  
- Exibe campos de **usuário** e **senha**  
- Após login bem-sucedido, redireciona o usuário para a página de consultas ou administração  
- Usa as funções do `backend.py` para validação  

#### 📊 `2_Página_de_Consultas.py`
- Acessível apenas para **usuários logados**  
- Permite visualizar dados e resultados armazenados  
- Pode exibir tabelas com **Pandas** ou dados processados no backend  

#### ⚙️ `3_Página_do_Administrador.py`
- Acesso restrito ao **usuário administrador**  
- Permite:
  - Criar novos usuários  
  - Excluir usuários existentes  
  - Ver a lista completa de contas  
- Opera inteiramente sobre as funções de `database.py`

---

## ▶️ Como Executar o Sistema

### 1️⃣ Criar o administrador (apenas na primeira execução)
```bash
python create_adm.py
```

### 2️⃣ Executar o aplicativo Streamlit
```bash
streamlit run 1_Página_de_Login.py
```

### 3️⃣ Acessar o sistema no navegador
Abra o endereço:
```
http://localhost:8501
```

### 4️⃣ Login
Use as credenciais do administrador criadas anteriormente.  
Após o login:
- **Usuários comuns** → acessam a página de consultas  
- **Administradores** → acessam também a página de administração  

---

## 🧰 Estrutura de Sessões e Permissões
O sistema usa o recurso de sessão do **Streamlit (`st.session_state`)** para:
- Armazenar o usuário atual  
- Controlar redirecionamentos entre páginas  
- Exibir elementos dinamicamente conforme o tipo de usuário (admin / comum)

#### Exemplo de verificação:
```python
if 'user' not in st.session_state:
    st.warning("Por favor, faça login primeiro.")
    st.stop()
```

---

## 💾 Persistência e Segurança
- Todas as senhas são armazenadas com **hash criptográfico** (nunca em texto puro).  
- O banco **SQLite (`users.db`)** é **local**, podendo ser movido ou substituído sem comprometer o sistema.  
- A estrutura foi projetada para permitir **migração futura para bancos SQL remotos** (PostgreSQL, MySQL, etc.) com mínimas alterações em `database.py`.

---

## 🧩 Conclusão
O **Management Knowledge** é um sistema modular, seguro e simples de expandir.  
Ele serve como base para qualquer aplicação que envolva **gestão de usuários, autenticação e visualização de dados** por meio de **interfaces web leves e interativas**.

---
