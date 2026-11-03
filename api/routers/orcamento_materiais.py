from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.dependencies.resource_access import obter_orcamento_do_usuario
from api.models.material import Material
from api.repositories import orcamento_material_repository as repo
from api.schemas.orcamento_material import (OrcamentoMaterialCreate,
                                            OrcamentoMaterialUpdate,
                                            OrcamentoMaterialResponse)

router = APIRouter(prefix="/orcamentos/{idorcamentos}/materiais",
                   tags=["Materiais do orçamento"],
                   dependencies=[Depends(get_usuario_atual)])


@router.post("/", response_model=OrcamentoMaterialResponse,
             status_code=status.HTTP_201_CREATED)
def adicionar(idorcamentos: int,
              dados: OrcamentoMaterialCreate,
              db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    if db.get(Material, dados.materiais_id) is None:
        raise HTTPException(404, "Material não encontrado.")
    return repo.adicionar_material(
        db,
        idorcamentos,
        dados.materiais_id,
        dados.quantidade,
    )


@router.get("/", response_model=list[OrcamentoMaterialResponse])
def listar(
        idorcamentos: int,
        db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    return repo.listar_por_orcamento(db, idorcamentos)


@router.patch("/{materiais_id}", response_model=OrcamentoMaterialResponse)
def atualizar(
        idorcamentos: int,
        materiais_id: int,
        dados: OrcamentoMaterialUpdate,
        db: Session = Depends(get_db),
        usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    item = repo.buscar(db, idorcamentos, materiais_id)
    if item is None:
        raise HTTPException(404, "Material não está no orçamento.")
    return repo.atualizar_quantidade(db, item, dados.quantidade)


@router.delete("/{materiais_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def excluir(idorcamentos: int,
            materiais_id: int,
            db: Session = Depends(get_db),
            usuario=Depends(get_usuario_atual)):
    obter_orcamento_do_usuario(db, idorcamentos, usuario.idusuarios)
    item = repo.buscar(db, idorcamentos, materiais_id)
    if item is None:
        raise HTTPException(404, "Material não está no orçamento.")
    repo.excluir(db, item)
