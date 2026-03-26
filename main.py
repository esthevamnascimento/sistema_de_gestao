from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import engine, Base
from routers import epi, fleet, inventory
from routers import epi, fleet, inventory, auth, dashboard, equipment, employee, tools, ssm, users


# Importando todas as nossas rotas modulares inventario
from routers import epi, fleet, inventory, auth

# Importando as rotas das dashboards
from routers import epi, fleet, inventory, auth, dashboard, equipment

# cria as tabelas no banco de dados automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title = "Sistemas de Gestão")

# incluindo as rotas modulares
app.include_router(auth.router)
app.include_router(epi.router)
app.include_router(dashboard.router)
app.include_router(fleet.router) # <-- Correção: Faltava isso para a API de frotas funcionar!
app.include_router(inventory.router) # <-- Correção: Faltava isso para a API de estoque funcionar!
app.include_router(equipment.router)
app.include_router(employee.router)
app.include_router(tools.router)
app.include_router(ssm.router)
app.include_router(users.router)

# configurando frontend
templates = Jinja2Templates(directory="templates")

@app.get("/") # <--- Agora o "/" abre o Dashboard
def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/login") 
def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/epis")
def read_root(request: Request):
    return templates.TemplateResponse("epis.html", {"request": request})

@app.get("/frotas")
def read_frotas(request: Request):
    return templates.TemplateResponse("frotas.html", {"request": request})

@app.get("/estoque")
def read_estoque(request: Request):
    return templates.TemplateResponse("estoque.html", {"request": request})

@app.get("/equipamentos")
def read_equipamentos(request: Request):
    return templates.TemplateResponse("equipamentos.html", {"request": request})

@app.get("/funcionarios")
def read_funcionarios(request: Request):
    return templates.TemplateResponse("funcionarios.html", {"request": request})

@app.get("/pedidos-epi")
def read_pedidos_epi(request: Request):
    return templates.TemplateResponse("pedidos_epi.html", {"request": request})

@app.get("/ferramentas")
def read_ferramentas(request: Request):
    return templates.TemplateResponse("ferramentas.html", {"request": request})

@app.get("/ssm")
def read_ssm(request: Request):
    return templates.TemplateResponse("ssm.html", {"request": request})

@app.get("/usuarios")
def read_usuarios(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})

@app.get("/nav.html")
def read_nav(request: Request):
    return templates.TemplateResponse("nav.html", {"request": request})


import uvicorn

if __name__ == "__main__":
    # O host 0.0.0.0 abre para a rede, e a porta 80 é a porta padrão de internet
    uvicorn.run(app, host="0.0.0.0", port=80)


#para rodar: uvicorn main:app --reload