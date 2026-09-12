from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    UniqueConstraint,
)

from app.database import Base


class Pasajero(Base):
    __tablename__ = "pasajero"
    __table_args__ = (
        UniqueConstraint(
            "tipo_documento", "numero_documento", name="uq_pasajero_documento"
        ),
    )

    id_persona = Column(
        Integer,
        ForeignKey("persona.id_persona", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    tipo_documento = Column(
        Enum("DNI", "Pasaporte", "Carnet de Extranjeria", name="tipo_documento"),
        nullable=False,
    )
    numero_documento = Column(String(15), nullable=False)
    id_categoria = Column(
        Integer,
        ForeignKey("categoria_migratoria.id", ondelete="RESTRICT"),
        nullable=False,
    )
