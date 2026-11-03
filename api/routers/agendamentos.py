from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.models.agendamento import Agendamento
from api.models.orcamento import Orcamento
from api.repositories import agendamento_repository as repository
from api.schemas.agendamento import (
    AgendamentoCreate,
    AgendamentoResponse,
    AgendamentoUpdate,
)

router = APIRouter(prefix="/agendamentos",
                   tags=["Agendamentos"])


def obter_orcamento_do_usuario(
    db: Session, orcamentos_id: int, usuario_id: int
) -> Orcamento:
    orcamento = db.get(Orcamento, orcamentos_id)
    if orcamento is None or orcamento.usuarios_id != usuario_id:
        raise HTTPException(status_code=404,
                            detail="Orçamento não encontrado")
    return orcamento


def obter_agendamento_do_usuario(
    db: Session, idagendamentos: int, usuario_id: int
) -> Agendamento:
    item = repository.buscar_por_id(db, idagendamentos)
    if item is None:
        raise HTTPException(status_code=404,
                            detail="Agendamento não encontrado")
    obter_orcamento_do_usuario(db,
                               item.orcamentos_id,
                               usuario_id)
    return item


@router.post(
    "/",
    response_model=AgendamentoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_agendamento(
    dados: AgendamentoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    obter_orcamento_do_usuario(db,
                               dados.orcamentos_id,
                               usuario.idusuarios)

    existente = repository.obter_por_orcamento(db,
                                               dados.orcamentos_id)
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este orçamento já possui um agendamento",
        )

    try:
        return repository.criar(db, dados)
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este orçamento já possui um agendamento",
        ) from erro


@router.get("/", response_model=list[AgendamentoResponse])
def listar_agendamentos(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    from sqlalchemy import select

    ids = db.scalars(
        select(Orcamento.idorcamentos).where(
            Orcamento.usuarios_id == usuario.idusuarios
        )
    ).all()
    if not ids:
        return []
    return [
        item for item in repository.listar_ordenados(db)
        if item.orcamentos_id in ids
    ]


@router.get("/{idagendamentos}",
            response_model=AgendamentoResponse)
def obter_agendamento(
    idagendamentos: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    return obter_agendamento_do_usuario(db,
                                        idagendamentos,
                                        usuario.idusuarios)


@router.patch("/{idagendamentos}",
              response_model=AgendamentoResponse)
def atualizar_agendamento(
    idagendamentos: int,
    dados: AgendamentoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    item = obter_agendamento_do_usuario(db,
                                        idagendamentos,
                                        usuario.idusuarios)
    return repository.atualizar(db, item, dados)


@router.delete("/{idagendamentos}",
               status_code=status.HTTP_204_NO_CONTENT)
def excluir_agendamento(
    idagendamentos: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    item = obter_agendamento_do_usuario(db,
                                        idagendamentos,
                                        usuario.idusuarios)
    repository.excluir(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
