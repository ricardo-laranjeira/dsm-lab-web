from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.agendamento import Agendamento
from api.repositories.base_repository import BaseRepository


class AgendamentoRepository(
    BaseRepository[Agendamento]
):
    def __init__(self):
        super().__init__(Agendamento)

    def listar_ordenados(
        self,
        db: Session,
    ) -> list[Agendamento]:

        consulta = (
            select(Agendamento)
            .order_by(
                Agendamento.data,
                Agendamento.hora,
            )
        )

        return list(db.scalars(consulta).all())

    def obter_por_orcamento(
        self,
        db: Session,
        orcamentos_id: int,
    ) -> Agendamento | None:

        consulta = select(Agendamento).where(
            Agendamento.orcamentos_id == orcamentos_id
        )

        return db.scalar(consulta)


agendamento_repository = (
    AgendamentoRepository()
)
