from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.endereco import Endereco
from api.repositories.base_repository import BaseRepository
from api.schemas.endereco import EnderecoCreate


class EnderecoRepository(BaseRepository[Endereco]):

    def __init__(self):
        super().__init__(Endereco)

    def buscar_por_id_do_cliente(
        self,
        db: Session,
        idenderecos: int,
        cliente_id: int,
    ) -> Endereco | None:

        return db.scalar(
            select(Endereco).where(
                Endereco.idenderecos == idenderecos,
                Endereco.cliente_id == cliente_id,
            )
        )

    def listar_por_cliente(
        self,
        db: Session,
        cliente_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Endereco]:

        stmt = (
            select(Endereco)
            .where(Endereco.cliente_id == cliente_id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(stmt).all())

    def criar_para_cliente(
        self,
        db: Session,
        dados: EnderecoCreate,
        cliente_id: int,
    ) -> Endereco:

        endereco = Endereco(
            **dados.model_dump(),
            cliente_id=cliente_id,
        )

        return self._salvar(db, endereco)


endereco_repository = EnderecoRepository()
