from sqlalchemy import Column, Integer, Numeric, Enum, CheckConstraint

from app.database import Base


class CategoriaMigratoria(Base):
    __tablename__ = "categoria_migratoria"
    __table_args__ = (CheckConstraint("tarifa >= 0", name="chk_categoria_tarifa"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(
        Enum("Nacional", "Internacional", "Transito", name="nombre_categoria_migratoria"),
        nullable=False,
    )
    tarifa = Column(Numeric(10, 2), nullable=False)
