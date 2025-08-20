# create_admin.py
import database as db
db.criar_tabela_usuarios()
if db.adicionar_usuario('admin', 'admin123', 'adm'):
     print("Usuário 'admin' criado com sucesso!")
else:
     print("Usuário 'admin' já existe.")