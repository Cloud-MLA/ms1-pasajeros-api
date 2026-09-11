"""
Seed local para desarrollo y testing de MS1.

Inserta 3 categorías migratorias + ~5k pasajeros en la DB local.
NO reemplaza al seeds/ compartido de Dev D (aeropuerto-data-science/seeds/).

Uso:
    python -m app.scripts.seed_local
"""

import random
from datetime import date, timedelta

from sqlalchemy import text

from app.database import SessionLocal

CATEGORIAS = [
    {"nombre": "Nacional", "tarifa": 12.50},
    {"nombre": "Internacional", "tarifa": 38.45},
    {"nombre": "Transito", "tarifa": 18.00},
]

TIPOS_DOCUMENTO = ["DNI", "Pasaporte", "Carnet de Extranjeria"]

NOMBRES = [
    "Juan", "Maria", "Carlos", "Ana", "Luis", "Carmen", "Pedro", "Rosa",
    "Miguel", "Lucia", "Jorge", "Elena", "Fernando", "Patricia", "Ricardo",
    "Claudia", "Sergio", "Monica", "Andrea", "Roberto", "Laura", "Diego",
    "Sofia", "Manuel", "Valeria", "Alejandro", "Camila", "Daniel", "Isabella",
    "Francisco", "Martina", "Antonio", "Gabriela", "Jose", "Daniela", "Javier",
    "Paula", "Rafael", "Adriana", "David",
]

APELLIDOS = [
    "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez",
    "Diaz", "Cruz", "Morales", "Ortiz", "Gutierrez", "Chavez", "Ramos",
    "Ruiz", "Alvarez", "Mendoza", "Castillo", "Vargas", "Jimenez", "Moreno",
    "Romero", "Herrera", "Medina", "Aguilar", "Vega", "Castro", "Reyes",
    "Peña", "Guzman", "Acosta", "Miranda", "Campos", "Fuentes",
]

SEED = 42
NUM_PASAJEROS = 5000
ID_PERSONA_MIN = 100_000
ID_PERSONA_MAX = 160_000


def seed_categorias(db) -> dict:
    """Inserta las 3 categorías migratorias. Devuelve dict nombre->id."""
    categorias_map = {}
    for cat in CATEGORIAS:
        existing = db.execute(
            text("SELECT id FROM categoria_migratoria WHERE nombre = :nombre"),
            {"nombre": cat["nombre"]},
        ).fetchone()
        if existing:
            categorias_map[cat["nombre"]] = existing[0]
        else:
            db.execute(
                text(
                    "INSERT INTO categoria_migratoria (nombre, tarifa) "
                    "VALUES (:nombre, :tarifa)"
                ),
                cat,
            )
            db.flush()
            new_id = db.execute(
                text("SELECT id FROM categoria_migratoria WHERE nombre = :nombre"),
                {"nombre": cat["nombre"]},
            ).fetchone()[0]
            categorias_map[cat["nombre"]] = new_id
    db.commit()
    return categorias_map


def seed_pasajeros(db, categorias_map: dict, count: int = NUM_PASAJEROS):
    """Inserta pasajeros con IDs en rango 100k-160k."""
    rng = random.Random(SEED)
    existent_count = db.execute(text("SELECT COUNT(*) FROM persona")).fetchone()[0]
    if existent_count >= count:
        print(f"Ya hay {existent_count} personas, skip seed.")
        return

    ids_disponibles = list(range(ID_PERSONA_MIN, ID_PERSONA_MAX + 1))
    rng.shuffle(ids_disponibles)
    ids_a_usar = ids_disponibles[:count]

    categorias_nombre = list(categorias_map.keys())

    batch_size = 500
    insertados = 0

    for i in range(0, count, batch_size):
        batch = ids_a_usar[i : i + batch_size]
        personas_values = []
        pasajeros_values = []

        for id_persona in batch:
            nombre = rng.choice(NOMBRES)
            apellido = rng.choice(APELLIDOS)
            anio = rng.randint(1950, 2008)
            mes = rng.randint(1, 12)
            dia = rng.randint(1, 28)
            fecha_nac = date(anio, mes, dia)

            tipo_doc = rng.choice(TIPOS_DOCUMENTO)
            num_doc = str(rng.randint(10000000, 99999999))
            id_categoria = categorias_map[rng.choice(categorias_nombre)]

            personas_values.append(
                {
                    "id_persona": id_persona,
                    "nombre": nombre,
                    "apellido": apellido,
                    "fecha_nacimiento": fecha_nac,
                }
            )
            pasajeros_values.append(
                {
                    "id_persona": id_persona,
                    "tipo_documento": tipo_doc,
                    "numero_documento": num_doc,
                    "id_categoria": id_categoria,
                }
            )

        for p in personas_values:
            db.execute(
                text(
                    "INSERT IGNORE INTO persona (id_persona, nombre, apellido, fecha_nacimiento) "
                    "VALUES (:id_persona, :nombre, :apellido, :fecha_nacimiento)"
                ),
                p,
            )
        for p in pasajeros_values:
            db.execute(
                text(
                    "INSERT IGNORE INTO pasajero (id_persona, tipo_documento, numero_documento, id_categoria) "
                    "VALUES (:id_persona, :tipo_documento, :numero_documento, :id_categoria)"
                ),
                p,
            )

        db.commit()
        insertados += len(batch)
        print(f"  {insertados}/{count} pasajeros insertados...")

    total_p = db.execute(text("SELECT COUNT(*) FROM persona")).fetchone()[0]
    total_pa = db.execute(text("SELECT COUNT(*) FROM pasajero")).fetchone()[0]
    print(f"Seed completado: {total_p} personas, {total_pa} pasajeros.")


def main():
    print("=== Seed Local MS1 ===")
    db = SessionLocal()
    try:
        print("\n1. Categorías migratorias...")
        cat_map = seed_categorias(db)
        for nombre, id_ in cat_map.items():
            print(f"   {nombre} -> id={id_}")

        print(f"\n2. Pasajeros (~{NUM_PASAJEROS})...")
        seed_pasajeros(db, cat_map)
    finally:
        db.close()
    print("\nListo.")


if __name__ == "__main__":
    main()
