from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.models.cliente import Cliente
from api.repositories import orcamento_repository
from api.schemas.orcamento import (
    OrcamentoCreate,
    OrcamentoResponse,
    OrcamentoUpdate,
)

router = APIRouter(
    prefix="/orcamentos",
    tags=["Orçamentos"],
    dependencies=[Depends(get_usuario_atual)],
)


def _validar_cliente_do_usuario(
    db: Session, clientes_id: int, usuarios_id: int
) -> None:
    cliente = db.get(Cliente, clientes_id)
    if cliente is None or cliente.usuarios_id != usuarios_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
        )


@router.post(
    "/", response_model=OrcamentoResponse, status_code=status.HTTP_201_CREATED
)
def criar_orcamento(
    dados: OrcamentoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    _validar_cliente_do_usuario(db, dados.clientes_id, usuario.idusuarios)
    return orcamento_repository.criar_para_usuario(
        db,
        dados,
        usuario.idusuarios,
    )


@router.get("/", response_model=list[OrcamentoResponse])
def listar_orcamentos(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    return orcamento_repository.listar_por_usuario(
        db,
        usuario.idusuarios,
        offset,
        limit,
    )


@router.get("/{idorcamentos}", response_model=OrcamentoResponse)
def buscar_orcamento(
    idorcamentos: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    item = orcamento_repository.buscar_por_id_do_usuario(
        db, idorcamentos, usuario.idusuarios
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado.")
    return item


@router.patch("/{idorcamentos}", response_model=OrcamentoResponse)
def atualizar_orcamento(
    idorcamentos: int,
    dados: OrcamentoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    item = orcamento_repository.buscar_por_id_do_usuario(
        db, idorcamentos, usuario.idusuarios
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado.")

    if dados.clientes_id is not None:
        _validar_cliente_do_usuario(db, dados.clientes_id, usuario.idusuarios)

    return orcamento_repository.atualizar(db, item, dados)


@router.delete("/{idorcamentos}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_orcamento(
    idorcamentos: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    item = orcamento_repository.buscar_por_id_do_usuario(
        db, idorcamentos, usuario.idusuarios
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado.")
    orcamento_repository.excluir(db, item)
