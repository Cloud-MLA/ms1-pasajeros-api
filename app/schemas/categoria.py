from pydantic import BaseModel


class CategoriaMigratoriaBase(BaseModel):
    nombre: str
    tarifa: float


class CategoriaMigratoria(CategoriaMigratoriaBase):
    id: int

    class Config:
        from_attributes = True