from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.repositories.base_repository import BaseRepository

TModel = TypeVar("TModel")


class AssociacaoRepository(
    BaseRepository[TModel],
    Generic[TModel],
):
    def listar_por_orcamento(
        self,
        db: Session,
        orcamentos_id: int,
    ) -> list[TModel]:
        return list(
            db.scalars(
                select(self.model).where(
                    self.model.orcamentos_id == orcamentos_id
                )
            ).all()
        )

    def buscar(
        self,
        db: Session,
        orcamentos_id: int,
        item_id: int,
    ) -> TModel | None:
        return db.get(
            self.model,
            (orcamentos_id, item_id),
        )

    def atualizar_quantidade(
        self,
        db: Session,
        item: TModel,
        quantidade: int,
    ) -> TModel:
        item.quantidade = quantidade

        db.commit()
        db.refresh(item)

        return item
