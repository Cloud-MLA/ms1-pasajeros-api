from pydantic import BaseModel, Field


class CrearEquipajeRequest(BaseModel):
    id: str = Field(max_length=20)
    peso: float = Field(gt=0)
    id_persona: int
    id_vuelo: int


class Equipaje(BaseModel):
    id: str
    peso: float
    id_persona: int
    id_vuelo: int

    class Config:
        from_attributes = True
