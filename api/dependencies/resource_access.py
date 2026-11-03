from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.models.cliente import Cliente
from api.models.orcamento import Orcamento
from api.repositories import cliente_repository, orcamento_repository


def obter_cliente_do_usuario(
    db: Session,
    idclientes: int,
    usuario_id: int,
) -> Cliente:
    cliente = cliente_repository.buscar_por_id_do_usuario(
        db,
        idclientes,
        usuario_id,
    )
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
        )
    return cliente


def obter_orcamento_do_usuario(
    db: Session,
    idorcamentos: int,
    usuario_id: int,
) -> Orcamento:
    orcamento = orcamento_repository.buscar_por_id_do_usuario(
        db,
        idorcamentos,
        usuario_id,
    )
    if orcamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado.",
        )
    return orcamento
