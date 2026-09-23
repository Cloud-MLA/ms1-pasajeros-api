"""
Carga masiva de CSVs del generador compartido a la BD local (MySQL).

Requiere que `python seeds/generar.py --ms 2 && python seeds/generar.py --ms 1`
se haya corrido primero en aeropuerto-data-science/seeds/ y que los CSVs estén en
seeds/output/ms1/*.csv.

Uso (desde el host, con el compose local publicado en localhost:3306):
    DB_HOST=localhost DB_PORT=3306 DB_USER=... DB_PASSWORD=... DB_NAME=... \
        python -m app.scripts.load_csv
"""
import csv
import re
import sys
from pathlib import Path

from sqlalchemy import MetaData, Table, create_engine, text

from app.config import get_settings

OUTPUT_MS1 = (
    Path(__file__).resolve().parents[3]
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

BATCH = 5_000

# Normaliza fechas ISO 8601 (2026-08-28T05:07:00Z) a formato MySQL TIMESTAMP.
_ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _normalizar(valor: str) -> str:
    if isinstance(valor, str) and _ISO_DATETIME.match(valor):
        return valor.replace("T", " ").replace("Z", "")
    return valor


def _leer_csv(archivo: Path, columnas: list[str]) -> list[dict]:
    filas = []
    with archivo.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filas.append({c: _normalizar(row[c]) for c in columnas})
    return filas


def load_csv(engine, tabla: str, archivo: Path, columnas: list[str]) -> int:
    """Limpia la tabla y la repuebla con el CSV (inserción por lotes)."""
    if not archivo.exists():
        print(f"  SKIP {archivo.name}: no existe")
        return 0

    filas = _leer_csv(archivo, columnas)
    meta = MetaData()
    tbl = Table(tabla, meta, autoload_with=engine)

    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        conn.execute(text(f"TRUNCATE TABLE {tabla}"))
        for i in range(0, len(filas), BATCH):
            conn.execute(tbl.insert(), filas[i : i + BATCH])
        count = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    print(f"  {tabla}: {count} filas (fuente: {len(filas)})")
    return count


def main() -> None:
    if not OUTPUT_MS1.exists():
        print(f"ERROR: {OUTPUT_MS1} no existe")
        print("Corre primero en aeropuerto-data-science/seeds/:")
        print("  python seeds/generar.py --ms 2 && python seeds/generar.py --ms 1")
        sys.exit(1)

    print(f"Directorio CSVs: {OUTPUT_MS1}")

    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)

    total = 0
    try:
        for tabla, archivo, columnas in TABLAS_ORDEN:
            print(f"\nCargando {tabla}...")
            total += load_csv(engine, tabla, OUTPUT_MS1 / archivo, columnas)
        print(f"\nCarga completa: {total} filas totales.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()