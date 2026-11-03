from api.models.material import Material
from api.repositories.base_repository import BaseRepository


class MaterialRepository(
    BaseRepository[Material]
):
    def __init__(self):
        super().__init__(Material)


material_repository = MaterialRepository()
