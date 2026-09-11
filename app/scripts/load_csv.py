"""
Carga masiva de CSVs del generador compartido a la BD local (MySQL).

Requiere que `python generar.py --ms 2 && python generar.py --ms 1` se haya
corrido primero en aeropuerto-data-science/seeds/ y que los CSVs estén en
seeds/output/ms1/*.csv.

Uso:
    python -m app.scripts.load_csv
"""
import sys
from pathlib import Path

from sqlalchemy import text

from app.config import get_settings
from app.database import SessionLocal

OUTPUT_MS1 = (
    Path(__file__).resolve().parents[4]
    / "aeropuerto-data-science" / "seeds" / "output" / "ms1"
)

TABLAS_ORDEN = [
    ("categoria_migratoria", "categoria_migratoria.csv", ["id", "nombre", "tarifa"]),
    ("persona", "persona.csv", ["id_persona", "nombre", "apellido", "fecha_nacimiento"]),
    (
        "pasajero",
        "pasajero.csv",
        ["id_persona", "tipo_documento", "numero_documento", "id_categoria"],
    ),
    (
        "ticket",
        "ticket.csv",
        ["id_ticket", "precio", "fecha_emision", "estado_boarding", "id_vuelo", "id_persona"],
    ),
    ("checkin", "checkin.csv", ["id_ticket", "fecha_hora", "counter", "con_equipaje"]),
    ("equipaje", "equipaje.csv", ["id", "peso", "id_persona", "id_vuelo"]),
]


def load_csv(db, tabla: str, archivo: Path, columnas: list[str]) -> int:
    """Carga un CSV con LOAD DATA LOCAL INFILE. Devuelve filas en la tabla."""
    if not archivo.exists():
        print(f"  SKIP {archivo} no existe")
        return 0

    placeholders = ", ".join(f"@col{i}" for i in range(len(columnas)))
    set_clauses = ", ".join(f"{c} = @col{i}" for i, c in enumerate(columnas))

    sql = (
        f"LOAD DATA LOCAL INFILE :archivo "
        f"INTO TABLE {tabla} "
        f"FIELDS TERMINATED BY ',' ENCLOSED BY '\"' "
        f"LINES TERMINATED BY '\\n' "
        f"IGNORE 1 LINES "
        f"({placeholders}) "
        f"SET {set_clauses}"
    )

    db.execute(text("SET SESSION FOREIGN_KEY_CHECKS=0"))
    db.execute(text(f"TRUNCATE TABLE {tabla}"))
    db.execute(text(sql), {"archivo": str(archivo.resolve())})
    db.commit()
    db.execute(text("SET SESSION FOREIGN_KEY_CHECKS=1"))

    count = db.execute(text(f"SELECT COUNT(*) FROM {tabla}")).fetchone()[0]
    print(f"  {tabla}: {count} filas cargadas")
    return count


def main() -> None:
    csv_dir = OUTPUT_MS1 if OUTPUT_MS1.exists() else Path("seeds/output/ms1")
    print(f"Directorio CSVs: {csv_dir}")

    if not csv_dir.exists():
        print(f"ERROR: {csv_dir} no existe")
        print("Corre primero en aeropuerto-data-science/seeds/:")
        print("  python generar.py --ms 2 && python generar.py --ms 1")
        sys.exit(1)

    db = SessionLocal()
    try:
        total = 0
        for tabla, archivo, columnas in TABLAS_ORDEN:
            print(f"\nCargando {tabla}...")
            total += load_csv(db, tabla, csv_dir / archivo, columnas)
        print(f"\nCarga completa: {total} filas totales.")
    finally:
        db.close()


if __name__ == "__main__":
    main()