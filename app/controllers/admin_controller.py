# Rotas Accesiveis apenas para o Admin

from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session 

from app.database import get_db
from app.models.usuario import Usuario
from app.auth import get_admin, hash_senha

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

templates = Jinja2Templates(directory="app/templates")

# ROTA: GET /usuarios/
# OBJETIVO: Listar todos os usuários cadastrados e renderizar a tela principal (index).

@router.get("/")
def exibir_usuarios(
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin) , # Bloqueia o acesso para usuarios não autenticados ou sem privilégios de administrador
):
    # Buscar ususarios no banco de dados
    usuarios = db.query(Usuario).order_by(Usuario.nome).all()

    return templates.TemplateResponse(
        request,
        "usuarios/index.html",
        {
            "request": request,
            "usuario": admin, # Passa o usuário logado para o template
            "usuarios": usuarios
        }
    )

# ROTA: GET /usuarios/novo
# OBJETIVO: Renderizar a tela com o formulário em branco para criar um novo usuário.

@router.get("/novo", response_class=HTMLResponse)
def form_novo_usuario(request: Request, admin = Depends(get_admin)):
    return templates.TemplateResponse(
        request,
        "usuarios/novo.html", 
        {"request": request, "usuario": admin}
    )

# ROTA: POST /usuarios/novo
# OBJETIVO: Processar os dados do formulário de criação, validar se o e-mail é único e salvar o usuário no banco.

@router.post("/novo")
def salvar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    role: str = Form("user"),
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario_existente:
        return templates.TemplateResponse(
            request,
            "usuarios/novo.html", 
            {"request": request, "usuario": admin, "erro": "Este e-mail já está cadastrado."}
        )

    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_senha(senha),
        role=role,
        ativo=True
    )
    db.add(novo_usuario)
    db.commit()
    
    return RedirectResponse(url="/usuarios?criado=ok", status_code=status.HTTP_303_SEE_OTHER)

# ROTA: POST /usuarios/{id}/toggle-ativo
# OBJETIVO: Inverter o status do usuário (Ativar se estiver Inativo / Desativar se estiver Ativo), impedindo a auto-desativação.

@router.post("/{usuario_id}/toggle-ativo")
def toggle_usuario_ativo(
    usuario_id: int, 
    db: Session = Depends(get_db), 
    admin = Depends(get_admin)
):
    usuario_banco = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario_banco:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_303_SEE_OTHER)
        
    # Correção: Acessando o ID do admin como dicionário
    admin_id = admin.get("id") if isinstance(admin, dict) else admin.id
    
    if usuario_banco.id == admin_id:
        return RedirectResponse(url="/usuarios?erro=autoproprio", status_code=status.HTTP_303_SEE_OTHER)
        
    usuario_banco.ativo = not usuario_banco.ativo
    db.commit()
    
    return RedirectResponse(url="/usuarios", status_code=status.HTTP_303_SEE_OTHER)

# ROTA: GET /usuarios/{id}/editar
# OBJETIVO: Buscar os dados atuais de um usuário específico no banco e carregá-los no formulário de edição.

@router.get("/{usuario_id}/editar", response_class=HTMLResponse)
def form_editar_usuario(
    usuario_id: int, 
    request: Request, 
    db: Session = Depends(get_db), 
    admin = Depends(get_admin)
):
    usuario_editar = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_editar:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse(
        request,
        "usuarios/editar.html", 
        {"request": request, "usuario": admin, "usuario_editar": usuario_editar}
    )

# ROTA: POST /usuarios/{id}/editar
# OBJETIVO: Processar as alterações do formulário de edição, validar segurança/duplicidade de e-mail e salvar no banco.

@router.post("/{usuario_id}/editar")
def atualizar_usuario(
    usuario_id: int,
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(None), 
    role: str = Form(...),
    ativo: bool = Form(True),
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    usuario_banco = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_banco:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_303_SEE_OTHER)

    admin_id = admin.get("id") if isinstance(admin, dict) else admin.id
    if usuario_banco.id == admin_id and not ativo:
        return RedirectResponse(url="/usuarios?erro=autoproprio", status_code=status.HTTP_303_SEE_OTHER)

    email_dono = db.query(Usuario).filter(Usuario.email == email, Usuario.id != usuario_id).first()
    if email_dono:
        return templates.TemplateResponse(
            request,
            "usuarios/editar.html", 
            {"request": request, "usuario": admin, "usuario_editar": usuario_banco, "erro": "Este e-mail já está em uso por outro usuário."}
        )

    usuario_banco.nome = nome
    usuario_banco.email = email
    usuario_banco.role = role
    usuario_banco.ativo = ativo
    
    if senha:
        usuario_banco.senha_hash = hash_senha(senha)

    db.commit()
    return RedirectResponse(url="/usuarios?editado=ok", status_code=status.HTTP_303_SEE_OTHER)