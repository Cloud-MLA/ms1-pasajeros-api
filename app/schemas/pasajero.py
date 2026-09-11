from datetime import date

from pydantic import BaseModel, Field

from app.schemas.enums import TipoDocumento


class CrearPasajeroRequest(BaseModel):
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fecha_nacimiento: date
    tipo_documento: TipoDocumento
    numero_documento: str = Field(max_length=15)
    id_categoria: int


class PersonaConPasajero(BaseModel):
    id_persona: int
    nombre: str
    apellido: str
    fecha_nacimiento: date
    tipo_documento: TipoDocumento
    numero_documento: str
    id_categoria: int

    class Config:
        from_attributes = True
