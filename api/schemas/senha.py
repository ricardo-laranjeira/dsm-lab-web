
from pydantic import BaseModel, Field, model_validator


class SenhaUpdate(BaseModel):
    senha_atual: str = Field(min_length=1)
    nova_senha: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validar_senhas_diferentes(self):
        if self.senha_atual == self.nova_senha:
            raise ValueError(
                "A nova senha deve ser diferente da senha atual."
            )
        return self
