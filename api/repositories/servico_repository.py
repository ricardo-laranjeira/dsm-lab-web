from api.models.servico import Servico
from api.repositories.base_repository import BaseRepository


class ServicoRepository(
    BaseRepository[Servico]
):
    def __init__(self):
        super().__init__(Servico)


servico_repository = ServicoRepository()
