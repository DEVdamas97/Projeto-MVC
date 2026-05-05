# 1. Hash e verificação de senhas com bcrypt
# 2. Geração de tokens JWT
# 3. Leitura e validação do token vindo do cookie

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
import os

# Carregar variaveis de ambiente 

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM")


ACESS_TOKEN_EXPIRACAO_MINUTOS = os.getenv("ACESS_TOKEN_EXPIRACAO_MINUTOS")

# CryptContent

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_senha(senha:str):
    return pwd_context.hash(senha)

def verificar_senha(senha:str, senha_hash:str):
    return pwd_context.verify(senha, senha_hash)

# Funções do token 

def criar_token(data: dict):
    payload = data.copy()

    # Define quando o teken expira 
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACESS_TOKEN_EXPIRACAO_MINUTOS)
    payload.update({"exp": expira})

    # Criar o Token 
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decodificar_token(token:str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

# Dependencia do FastAPI

def get_usuario_logado(request:Request):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="não autenticado"
        )
    try:
        payload = decodificar_token(token)
        email= payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token invalido"
            )

            return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="tokan invalido ou expirado"
        )