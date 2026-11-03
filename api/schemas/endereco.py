from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EnderecoBase(BaseModel):
    cep: str = Field(min_length=1, max_length=10)
    endereco: str = Field(min_length=1, max_length=100)
    numero: str = Field(min_length=1, max_length=5)
    complemento: str | None = Field(default=None, max_length=100)
    bairro: str = Field(min_length=1, max_length=100)
    cidade: str = Field(min_length=1, max_length=45)
    estado: str = Field(min_length=1, max_length=45)


class EnderecoCreate(EnderecoBase):
    pass


class EnderecoUpdate(BaseModel):
    cep: str | None = Field(default=None, min_length=1, max_length=10)
    endereco: str | None = Field(default=None, min_length=1, max_length=100)
    numero: str | None = Field(default=None, min_length=1, max_length=5)
    complemento: str | None = Field(default=None, max_length=100)
    bairro: str | None = Field(default=None, min_length=1, max_length=100)
    cidade: str | None = Field(default=None, min_length=1, max_length=45)
    estado: str | None = Field(default=None, min_length=1, max_length=45)


class EnderecoResponse(EnderecoBase):
    model_config = ConfigDict(from_attributes=True)
    idenderecos: int
    cliente_id: int
    data_cadastro: datetime
    data_atualizacao: datetime | None = None
