from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.categoria_migratoria import CategoriaMigratoria
from app.schemas.categoria import CategoriaMigratoria as CategoriaMigratoriaSchema

router = APIRouter(prefix="/categorias-migratorias", tags=["Categorias Migratorias"])


@router.get("", response_model=list[CategoriaMigratoriaSchema])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(CategoriaMigratoria).all()
