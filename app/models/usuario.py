from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func 
from app.database import Base

#Cria tabela usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nome = Column(String(100), nullable=False)

    email = Column(String(100), unique=True, index=True, nullable=False)

    senha_hash = Column(String(255), nullable=False)

    #Perfil do usuário: admin ou operador 
    role = Column(String(20), nullable=False, default="operador")

    ativo = Column(Boolean, default=True)

    #preenchido automatico pelo banco de dados ao criar o registro
    criando_em = Column(DateTime, server_default=func.now())
