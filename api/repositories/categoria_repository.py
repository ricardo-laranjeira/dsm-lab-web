from api.models.categoria import Categoria
from api.repositories.base_repository import BaseRepository


class CategoriaRepository(
    BaseRepository[Categoria]
):
    def __init__(self):
        super().__init__(Categoria)


categoria_repository = CategoriaRepository()
