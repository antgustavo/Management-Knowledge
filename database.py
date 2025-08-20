import sqlite3
import bcrypt

# --- Funções do Banco de Dados ---

def conectar():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect('users.db')

def criar_tabela_usuarios():
    """Cria a tabela de usuários se ela não existir."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_usuario(username, password, role):
    """Adiciona um novo usuário ao banco de dados com senha hasheada."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Gera o hash da senha
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash.decode('utf-8'), role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Erro ocorre se o username já existir
        return False
    finally:
        conn.close()

def verificar_usuario(username, password):
    """Verifica as credenciais do usuário."""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash, role FROM usuarios WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        password_hash_from_db = user_data[0].encode('utf-8')
        role = user_data[1]
        # Verifica se a senha fornecida corresponde ao hash no banco
        if bcrypt.checkpw(password.encode('utf-8'), password_hash_from_db):
            return {"role": role, "username": username}
            
    return None