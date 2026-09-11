"""Fixtures compartidos para la suite de tests de MS1.

Usa SQLite in-memory con StaticPool para que todas las sesiones
compartan la misma conexión (necesario para que las tablas persistan).
"""
from datetime import date
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# ---------- Engine SQLite in-memory con StaticPool ----------
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------- Tablas auxiliares (sin Enum de MySQL) ----------
def _create_test_tables():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categoria_migratoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tarifa REAL NOT NULL CHECK(tarifa >= 0)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS persona (
                id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                fecha_nacimiento DATE NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pasajero (
                id_persona INTEGER PRIMARY KEY,
                tipo_documento TEXT NOT NULL,
                numero_documento TEXT NOT NULL,
                id_categoria INTEGER NOT NULL,
                UNIQUE(tipo_documento, numero_documento),
                FOREIGN KEY(id_persona) REFERENCES persona(id_persona) ON DELETE CASCADE,
                FOREIGN KEY(id_categoria) REFERENCES categoria_migratoria(id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ticket (
                id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
                precio REAL NOT NULL,
                fecha_emision DATE NOT NULL,
                estado_boarding TEXT NOT NULL DEFAULT 'Emitido',
                id_vuelo INTEGER NOT NULL,
                id_persona INTEGER NOT NULL,
                FOREIGN KEY(id_persona) REFERENCES persona(id_persona)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS checkin (
                id_ticket INTEGER PRIMARY KEY,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                counter TEXT,
                con_equipaje INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(id_ticket) REFERENCES ticket(id_ticket) ON DELETE CASCADE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS equipaje (
                id TEXT PRIMARY KEY,
                peso REAL NOT NULL CHECK(peso > 0),
                id_persona INTEGER NOT NULL,
                id_vuelo INTEGER NOT NULL,
                FOREIGN KEY(id_persona) REFERENCES persona(id_persona)
            )
        """))


@pytest.fixture(autouse=True)
def setup_db():
    """Crea tablas antes de cada test y las borra después."""
    _create_test_tables()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Sesión de SQLAlchemy para tests directos."""
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    """TestClient de FastAPI con la sesión de test y MS2 mockeado."""
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------- Helpers para crear datos de prueba ----------

def crear_categoria(db, nombre="Nacional", tarifa=12.50):
    db.execute(
        text("INSERT INTO categoria_migratoria (nombre, tarifa) VALUES (:n, :t)"),
        {"n": nombre, "t": tarifa},
    )
    db.commit()
    return db.execute(text("SELECT id FROM categoria_migratoria WHERE nombre = :n"), {"n": nombre}).fetchone()[0]


def crear_persona(db, id_persona=None, nombre="Juan", apellido="Garcia", fecha_nac=None):
    if fecha_nac is None:
        fecha_nac = date(1990, 5, 15)
    if id_persona is not None:
        db.execute(
            text("INSERT INTO persona (id_persona, nombre, apellido, fecha_nacimiento) "
                 "VALUES (:id, :n, :a, :f)"),
            {"id": id_persona, "n": nombre, "a": apellido, "f": fecha_nac},
        )
    else:
        db.execute(
            text("INSERT INTO persona (nombre, apellido, fecha_nacimiento) "
                 "VALUES (:n, :a, :f)"),
            {"n": nombre, "a": apellido, "f": fecha_nac},
        )
    db.commit()
    if id_persona is not None:
        return id_persona
    return db.execute(text("SELECT last_insert_rowid()")).fetchone()[0]


def crear_pasajero(db, id_persona, tipo_documento="DNI", numero_documento=None, id_categoria=None):
    if id_categoria is None:
        id_categoria = crear_categoria(db)
    if numero_documento is None:
        numero_documento = f"{id_persona:08d}"
    db.execute(
        text("INSERT INTO pasajero (id_persona, tipo_documento, numero_documento, id_categoria) "
             "VALUES (:id, :td, :nd, :ic)"),
        {"id": id_persona, "td": tipo_documento, "nd": numero_documento, "ic": id_categoria},
    )
    db.commit()


def crear_ticket(db, id_ticket=None, precio=250.00, id_vuelo=1, id_persona=None, estado="Emitido"):
    if id_persona is None:
        id_persona = crear_persona(db)
    if id_ticket is not None:
        db.execute(
            text("INSERT INTO ticket (id_ticket, precio, fecha_emision, estado_boarding, id_vuelo, id_persona) "
                 "VALUES (:id, :p, DATE('now'), :e, :v, :ip)"),
            {"id": id_ticket, "p": precio, "e": estado, "v": id_vuelo, "ip": id_persona},
        )
    else:
        db.execute(
            text("INSERT INTO ticket (precio, fecha_emision, estado_boarding, id_vuelo, id_persona) "
                 "VALUES (:p, DATE('now'), :e, :v, :ip)"),
            {"p": precio, "e": estado, "v": id_vuelo, "ip": id_persona},
        )
    db.commit()
    if id_ticket is not None:
        return id_ticket
    return db.execute(text("SELECT last_insert_rowid()")).fetchone()[0]


# ---------- Mock de MS2 ----------

def mock_vuelo_exists_ok(id_vuelo: int):
    return {"exists": True, "id_vuelo": id_vuelo, "estado": "Programado"}


def mock_vuelo_exists_cancelado(id_vuelo: int):
    return {"exists": True, "id_vuelo": id_vuelo, "estado": "Cancelado"}


def mock_vuelo_no_existe(id_vuelo: int):
    return None
