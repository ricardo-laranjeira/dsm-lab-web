from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

TModel = TypeVar("TModel")


class BaseRepository(Generic[TModel]):
    def __init__(self, model: type[TModel]):
        self.model = model

    def listar(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100
    ) -> list[TModel]:
        return list(
            db.scalars(
                select(self.model)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def buscar_por_id(
        self,
        db: Session,
        id_: int,
    ) -> TModel | None:
        return db.get(self.model, id_)

    def criar(
        self,
        db: Session,
        dados: BaseModel,
    ) -> TModel:
        item = self.model(**dados.model_dump())

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    def atualizar(
        self,
        db: Session,
        item: TModel,
        dados: BaseModel,
    ) -> TModel:
        for campo, valor in dados.model_dump(
            exclude_unset=True
        ).items():
            setattr(item, campo, valor)

        db.commit()
        db.refresh(item)

        return item

    def excluir(
        self,
        db: Session,
        item: TModel,
    ) -> None:
        db.delete(item)
        db.commit()

    def _salvar(
            self,
            db: Session,
            item: TModel,
    ) -> TModel:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
