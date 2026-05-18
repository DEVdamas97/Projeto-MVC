# Arquivo para popular o banco de dados com usuários

from app.database import Session, engine, Base
from app.models.usuario import Usuario
from app.auth import hash_senha 

usuarios = [
    {
        "nome": "Admin",
        "email": "admin@teste.com",
        "senha": "admin1234",
        "role": "admin",
    },
    
    {
        "nome": "Admin",
        "email": "gabriel@admin.com",
        "senha": "admin1234",
        "role": "admin",
    },
]

def criar_usuarios():
    db = Session()

    try:
        for usuario in usuarios:
            usuario_existente = db.query(Usuario).filter_by(email=usuario["email"]).first()

            if usuario_existente:
                print(f"Usuário com email {usuario['email']} já existe no banco de dados.")
                continue

            else:
                novo_usuario = Usuario(
                    nome=usuario["nome"],
                    email=usuario["email"],
                    senha_hash=hash_senha(usuario["senha"]),
                    role=usuario["role"] 
                )
                db.add(novo_usuario)
        db.commit()
        print("Usuarios cadastrados com sucesso!")
    except Exception as erro:
        rollback = db.rollback()
        print(erro)
    finally:
        db.close()


# chama a função para criar os usuários
criar_usuarios()