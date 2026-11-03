from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.dependencies.resource_access import obter_cliente_do_usuario
from api.models.usuario import Usuario
from api.repositories import endereco_repository
from api.schemas.endereco import EnderecoCreate, EnderecoResponse, EnderecoUpdate

router = APIRouter(prefix="/clientes/{idclientes}/enderecos", tags=["Endereços"])


@router.post("/", response_model=EnderecoResponse, status_code=status.HTTP_201_CREATED)
def criar_endereco(
    idclientes: int, dados: EnderecoCreate,
    db: Session = Depends(get_db),
        usuario: Usuario = Depends(get_usuario_atual)):
    cliente = obter_cliente_do_usuario(db, idclientes, usuario.idusuarios)
    return endereco_repository.criar_para_cliente(
        db,
        dados,
        cliente.idclientes,
    )


@router.get("/", response_model=list[EnderecoResponse])
def listar_enderecos(idclientes: int, offset: int = Query(0, ge=0),
                     limit: int = Query(100, ge=1, le=100),
                     db: Session = Depends(get_db),
                     usuario: Usuario = Depends(get_usuario_atual)):
    cliente = obter_cliente_do_usuario(db, idclientes, usuario.idusuarios)
    return endereco_repository.listar_por_cliente(
        db,
        cliente.idclientes,
        offset,
        limit,
    )


@router.get("/{idenderecos}", response_model=EnderecoResponse)
def buscar_endereco(idclientes: int, idenderecos: int, db: Session = Depends(get_db),
                    usuario: Usuario = Depends(get_usuario_atual)):
    cliente = obter_cliente_do_usuario(db, idclientes, usuario.idusuarios)
    endereco = endereco_repository.buscar_por_id_do_cliente(
        db,
        idenderecos,
        cliente.idclientes,
    )
    if endereco is None:
        raise HTTPException(status_code=404, detail="Endereço não encontrado.")
    return endereco


@router.patch("/{idenderecos}", response_model=EnderecoResponse)
def atualizar_endereco(idclientes: int, idenderecos: int, dados: EnderecoUpdate,
                       db: Session = Depends(get_db),
                       usuario: Usuario = Depends(get_usuario_atual)):
    cliente = obter_cliente_do_usuario(db, idclientes, usuario.idusuarios)
    endereco = endereco_repository.buscar_por_id_do_cliente(
        db,
        idenderecos,
        cliente.idclientes,
    )
    if endereco is None:
        raise HTTPException(status_code=404, detail="Endereço não encontrado.")
    return endereco_repository.atualizar(db, endereco, dados)


@router.delete("/{idenderecos}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_endereco(idclientes: int, idenderecos: int, db: Session = Depends(get_db),
                     usuario: Usuario = Depends(get_usuario_atual)):
    cliente = obter_cliente_do_usuario(db, idclientes, usuario.idusuarios)
    endereco = endereco_repository.buscar_por_id_do_cliente(
        db,
        idenderecos,
        cliente.idclientes,
    )
    if endereco is None:
        raise HTTPException(status_code=404, detail="Endereço não encontrado.")
    endereco_repository.excluir(db, endereco)
