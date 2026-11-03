from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.cliente import Cliente
from api.repositories.base_repository import BaseRepository
from api.schemas.cliente import ClienteCreate, ClienteUpdate


class ClienteRepository(BaseRepository[Cliente]):

    def __init__(self):
        super().__init__(Cliente)

    def buscar_por_id_do_usuario(
        self,
        db: Session,
        idclientes: int,
        usuarios_id: int,
    ) -> Cliente | None:
        return db.scalar(
            select(Cliente).where(
                Cliente.idclientes == idclientes,
                Cliente.usuarios_id == usuarios_id,
            )
        )

    def listar_por_usuario(
        self,
        db: Session,
        usuarios_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Cliente]:

        stmt = (
            select(Cliente)
            .where(Cliente.usuarios_id == usuarios_id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(stmt).all())

    def criar_para_usuario(
        self,
        db: Session,
        dados: ClienteCreate,
        usuarios_id: int,
    ) -> Cliente:

        cliente = Cliente(
            **dados.model_dump(),
            usuarios_id=usuarios_id,
        )

        return self._salvar(db, cliente)

    def atualizar(
        self,
        db: Session,
        item: Cliente,
        dados: ClienteUpdate,
    ) -> Cliente:

        return super().atualizar(
            db,
            item,
            dados,
        )


cliente_repository = ClienteRepository()
