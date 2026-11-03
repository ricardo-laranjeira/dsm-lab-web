
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=45)
    email: EmailStr = Field(max_length=100)
    senha: str = Field(min_length=8, max_length=128)


class UsuarioResponse(BaseModel):
    idusuarios: int
    nome: str
    email: EmailStr
    ativo: bool
    data_cadastro: datetime
    data_atualizacao: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str | None = Field(default=None, min_length=1, max_length=45)
    email: EmailStr | None = Field(default=None, max_length=100)
    ativo: bool | None = None


class UsuarioPerfilUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=45,
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=100,
    )
