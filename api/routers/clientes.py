from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.dependencies.resource_access import obter_cliente_do_usuario
from api.models.usuario import Usuario
from api.repositories import cliente_repository
from api.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(dados: ClienteCreate, db: Session = Depends(get_db),
                  usuario: Usuario = Depends(get_usuario_atual)):
    return cliente_repository.criar_para_usuario(
        db,
        dados,
        usuario.idusuarios,
    )


@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100),
                    db: Session = Depends(get_db),
                    usuario: Usuario = Depends(get_usuario_atual)):
    return cliente_repository.listar_por_usuario(
        db,
        usuario.idusuarios,
        offset,
        limit,
    )


@router.get("/{idclientes}", response_model=ClienteResponse)
def buscar_cliente(idclientes: int, db: Session = Depends(get_db),
                   usuario: Usuario = Depends(get_usuario_atual)):
    return obter_cliente_do_usuario(
        db,
        idclientes,
        usuario.idusuarios,
    )


@router.patch("/{idclientes}", response_model=ClienteResponse)
def atualizar_cliente(
    idclientes: int,
    dados: ClienteUpdate, db: Session = Depends(get_db),
        usuario: Usuario = Depends(get_usuario_atual)):
    cliente = obter_cliente_do_usuario(
        db,
        idclientes,
        usuario.idusuarios,
    )
    return cliente_repository.atualizar(db, cliente, dados)


@router.delete("/{idclientes}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cliente(idclientes: int, db: Session = Depends(get_db),
                    usuario: Usuario = Depends(get_usuario_atual)):
    cliente = obter_cliente_do_usuario(
        db,
        idclientes,
        usuario.idusuarios,
    )
    cliente_repository.excluir(db, cliente)
