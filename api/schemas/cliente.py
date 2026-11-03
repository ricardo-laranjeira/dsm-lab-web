from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ClienteBase(BaseModel):
    nome: str = Field(min_length=1, max_length=45)
    telefone: str = Field(min_length=1, max_length=16)
    ativo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=45)
    telefone: str | None = Field(default=None, min_length=1, max_length=16)
    ativo: bool | None = None


class ClienteResponse(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    idclientes: int
    usuarios_id: int
    data_cadastro: datetime
    data_atualizacao: datetime | None = None
