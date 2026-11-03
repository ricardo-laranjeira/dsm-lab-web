
from fastapi import FastAPI

from api.routers.usuarios import router as usuarios_router
from api.routers.clientes import router as clientes_router
from api.routers.enderecos import router as enderecos_router
from api.routers.categorias import router as categorias_router
from api.routers.materiais import router as materiais_router
from api.routers.servicos import router as servicos_router
from api.routers.orcamentos import router as orcamentos_router
from api.routers.orcamento_materiais import router as orcamento_materiais_router
from api.routers.orcamento_servicos import router as orcamento_servicos_router
from api.routers.agendamentos import router as agendamentos_router

from api.routers.auth import router as auth_router


app = FastAPI(
    title="API de Orçamentos",
    description="API para gerenciamento de usuários e orçamentos.",
    version="1.0.0",
)

app.include_router(usuarios_router)
app.include_router(clientes_router)
app.include_router(enderecos_router)
app.include_router(categorias_router)
app.include_router(materiais_router)
app.include_router(servicos_router)
app.include_router(orcamentos_router)
app.include_router(orcamento_materiais_router)
app.include_router(orcamento_servicos_router)
app.include_router(agendamentos_router)
app.include_router(auth_router)


@app.get("/", tags=["Geral"])
def home():
    return {"mensagem": "API de Orçamentos funcionando."}
