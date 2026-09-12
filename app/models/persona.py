from sqlalchemy import Column, Integer, String, Date

from app.database import Base


class Persona(Base):
    __tablename__ = "persona"

    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
