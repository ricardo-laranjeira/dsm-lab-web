from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.repositories.categoria_repository import categoria_repository
from api.repositories.material_repository import material_repository
from api.schemas.material import MaterialCreate, MaterialResponse, MaterialUpdate

router = APIRouter(prefix="/materiais", tags=["Materiais"],
                   dependencies=[Depends(get_usuario_atual)])


def _validar_categoria(db: Session, categorias_id: int) -> None:
    if categoria_repository.buscar_por_id(db, categorias_id) is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def criar_material(dados: MaterialCreate, db: Session = Depends(get_db)):
    _validar_categoria(db, dados.categorias_id)
    return material_repository.criar(db, dados)


@router.get("/", response_model=list[MaterialResponse])
def listar_materiais(offset: int = Query(0, ge=0),
                     limit: int = Query(100, ge=1, le=100),
                     db: Session = Depends(get_db)):
    return material_repository.listar(db, offset, limit)


@router.get("/{idmateriais}", response_model=MaterialResponse)
def buscar_material(idmateriais: int, db: Session = Depends(get_db)):
    item = material_repository.buscar_por_id(db, idmateriais)
    if item is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    return item


@router.patch("/{idmateriais}", response_model=MaterialResponse)
def atualizar_material(idmateriais: int, dados: MaterialUpdate,
                       db: Session = Depends(get_db)):
    item = material_repository.buscar_por_id(db, idmateriais)
    if item is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    if dados.categorias_id is not None:
        _validar_categoria(db, dados.categorias_id)
    return material_repository.atualizar(db, item, dados)


@router.delete("/{idmateriais}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_material(idmateriais: int, db: Session = Depends(get_db)):
    item = material_repository.buscar_por_id(db, idmateriais)
    if item is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    material_repository.excluir(db, item)
