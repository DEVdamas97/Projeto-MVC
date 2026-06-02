from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.auth import get_usuario_opcional

from app.controllers import auth_controller
from app.controllers import admin_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacao_controllers
from app.controllers import cliente_controller
from app.controllers import pdv_controller

app = FastAPI(title="Sistema estoque")

#Configurar o Fastapi para servir os arquivos estáticos (CSS, JS, Imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

#Inclui os routers dos controles
app.include_router(auth_controller.router)
app.include_router(admin_controller.router)
app.include_router(categoria_controller.router)
app.include_router(movimentacao_controllers.router)
app.include_router(produto_controller.router)
app.include_router(cliente_controller.router)
app.include_router(pdv_controller.router)


#Tela inicial
@app.get("/")
def home(
    request: Request, 
    usuario = Depends(get_usuario_opcional)
    ):

    # Não logado - exibir página pública
    if usuario is None:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"request": request}
        )
    
    #Logado - exibir a tela principal com os dados do usuário
    return templates.TemplateResponse(
            request,
            "home.html",
            {"request": request, "usuario": usuario}
        )