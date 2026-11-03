from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.dependencies.auth import get_usuario_atual
from api.repositories.categoria_repository import categoria_repository
from api.schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["Categorias"],
                   dependencies=[Depends(get_usuario_atual)])


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(dados: CategoriaCreate, db: Session = Depends(get_db)):
    return categoria_repository.criar(db, dados)


@router.get("/", response_model=list[CategoriaResponse])
def listar_categorias(offset: int = Query(0, ge=0),
                      limit: int = Query(100, ge=1, le=100),
                      db: Session = Depends(get_db)):
    return categoria_repository.listar(db, offset, limit)


@router.get("/{idcategorias}", response_model=CategoriaResponse)
def buscar_categoria(idcategorias: int, db: Session = Depends(get_db)):
    item = categoria_repository.buscar_por_id(db, idcategorias)
    if item is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    return item


@router.patch("/{idcategorias}", response_model=CategoriaResponse)
def atualizar_categoria(idcategorias: int, dados: CategoriaUpdate,
                        db: Session = Depends(get_db)):
    item = categoria_repository.buscar_por_id(db, idcategorias)
    if item is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    return categoria_repository.atualizar(db, item, dados)


@router.delete("/{idcategorias}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_categoria(idcategorias: int, db: Session = Depends(get_db)):
    item = categoria_repository.buscar_por_id(db, idcategorias)
    if item is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    categoria_repository.excluir(db, item)
