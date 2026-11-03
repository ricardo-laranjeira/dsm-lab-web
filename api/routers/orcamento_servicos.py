from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.dependencies.resource_access import obter_orcamento_do_usuario
from api.models.servico import Servico
from api.repositories import orcamento_servico_repository as repo
from api.schemas.orcamento_servico import (OrcamentoServicoCreate,
                                           OrcamentoServicoUpdate,
                                           OrcamentoServicoResponse)

router = APIRouter(prefix="/orcamentos/{idorcamentos}/servicos",
                   tags=["Serviços do orçamento"],
                   dependencies=[Depends(get_usuario_atual)])


@router.post("/", response_model=OrcamentoServicoResponse,
             status_code=status.HTTP_201_CREATED)
def adicionar(idorcamentos: int,
              dados: OrcamentoServicoCreate,
              db: Session = Depends(get_db),
              usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    if db.get(Servico, dados.servicos_id) is None:
        raise HTTPException(404, "Serviço não encontrado.")
    return repo.adicionar_servico(
        db,
        idorcamentos,
        dados.servicos_id,
        dados.quantidade,
    )


@router.get("/", response_model=list[OrcamentoServicoResponse])
def listar(idorcamentos: int,
           db: Session = Depends(get_db),
           usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    return repo.listar_por_orcamento(db, idorcamentos)


@router.patch("/{servicos_id}", response_model=OrcamentoServicoResponse)
def atualizar(idorcamentos: int,
              servicos_id: int,
              dados: OrcamentoServicoUpdate,
              db: Session = Depends(get_db),
              usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    item = repo.buscar(db, idorcamentos, servicos_id)
    if item is None:
        raise HTTPException(404, "Serviço não está no orçamento.")
    return repo.atualizar_quantidade(db, item, dados.quantidade)


@router.delete("/{servicos_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def excluir(idorcamentos: int,
            servicos_id: int,
            db: Session = Depends(get_db),
            usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    item = repo.buscar(db, idorcamentos, servicos_id)
    if item is None:
        raise HTTPException(404, "Serviço não está no orçamento.")
    repo.excluir(db, item)
