from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    descricao: str = Field(min_length=1, max_length=45)


class CategoriaUpdate(BaseModel):
    descricao: str | None = Field(default=None, min_length=1, max_length=45)


class CategoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    idcategorias: int
    descricao: str
    data_cadastro: datetime
    data_atualizacao: datetime | None = None
