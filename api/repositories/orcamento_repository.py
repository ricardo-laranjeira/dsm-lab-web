from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.orcamento import Orcamento
from api.repositories.base_repository import BaseRepository
from api.schemas.orcamento import OrcamentoCreate


class OrcamentoRepository(BaseRepository[Orcamento]):

    def __init__(self):
        super().__init__(Orcamento)

    def listar_por_usuario(
        self,
        db: Session,
        usuarios_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Orcamento]:

        consulta = (
            select(Orcamento)
            .where(Orcamento.usuarios_id == usuarios_id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(consulta).all())

    def buscar_por_id_do_usuario(
        self,
        db: Session,
        idorcamentos: int,
        usuarios_id: int,
    ) -> Orcamento | None:

        consulta = select(Orcamento).where(
            Orcamento.idorcamentos == idorcamentos,
            Orcamento.usuarios_id == usuarios_id,
        )

        return db.scalars(consulta).first()

    def criar_para_usuario(
        self,
        db: Session,
        dados: OrcamentoCreate,
        usuarios_id: int,
    ) -> Orcamento:

        item = Orcamento(
            validade=dados.validade,
            status=dados.status,
            clientes_id=dados.clientes_id,
            usuarios_id=usuarios_id,
        )

        return self._salvar(db, item)


orcamento_repository = OrcamentoRepository()
