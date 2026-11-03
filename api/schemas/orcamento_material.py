from pydantic import BaseModel, ConfigDict, Field


class OrcamentoMaterialCreate(BaseModel):
    materiais_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class OrcamentoMaterialUpdate(BaseModel):
    quantidade: int = Field(gt=0)


class OrcamentoMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    orcamentos_id: int
    materiais_id: int
    quantidade: int
