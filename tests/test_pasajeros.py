"""Tests para los endpoints de pasajeros (POST, GET, búsqueda)."""
from unittest.mock import patch

from tests.conftest import (
    client, db, crear_categoria, crear_persona, crear_pasajero,
)


# ===================== POST /pasajeros =====================

def test_crear_pasajero_ok(client, db):
    cat_id = crear_categoria(db)
    payload = {
        "nombre": "Maria",
        "apellido": "Lopez",
        "fecha_nacimiento": "1995-03-20",
        "tipo_documento": "DNI",
        "numero_documento": "87654321",
        "id_categoria": cat_id,
    }
    resp = client.post("/pasajeros", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["nombre"] == "Maria"
    assert data["tipo_documento"] == "DNI"
    assert "id_persona" in data


def test_crear_pasajero_documento_duplicado(client, db):
    cat_id = crear_categoria(db)
    payload = {
        "nombre": "Carlos",
        "apellido": "Perez",
        "fecha_nacimiento": "1988-07-10",
        "tipo_documento": "DNI",
        "numero_documento": "11223344",
        "id_categoria": cat_id,
    }
    resp1 = client.post("/pasajeros", json=payload)
    assert resp1.status_code == 201

    payload2 = payload.copy()
    payload2["nombre"] = "Otra"
    resp2 = client.post("/pasajeros", json=payload2)
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "DUPLICADO"


def test_crear_pasajero_categoria_no_existe(client, db):
    payload = {
        "nombre": "Ana",
        "apellido": "Torres",
        "fecha_nacimiento": "2000-01-01",
        "tipo_documento": "Pasaporte",
        "numero_documento": "AB1234567",
        "id_categoria": 999,
    }
    resp = client.post("/pasajeros", json=payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "CATEGORIA_NO_EXISTE"


def test_crear_pasajero_enum_invalido(client, db):
    cat_id = crear_categoria(db)
    payload = {
        "nombre": "Pedro",
        "apellido": "Rios",
        "fecha_nacimiento": "1992-12-05",
        "tipo_documento": "INVALIDO",
        "numero_documento": "99887766",
        "id_categoria": cat_id,
    }
    resp = client.post("/pasajeros", json=payload)
    assert resp.status_code == 422


# ===================== GET /pasajeros/{id} =====================

def test_obtener_pasajero_ok(client, db):
    cat_id = crear_categoria(db)
    pid = crear_persona(db, nombre="Laura")
    crear_pasajero(db, pid, id_categoria=cat_id)

    resp = client.get(f"/pasajeros/{pid}")
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Laura"


def test_obtener_pasajero_no_existe(client):
    resp = client.get("/pasajeros/99999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NO_ENCONTRADO"


# ===================== GET /pasajeros?tipo_documento=&numero_documento= =====================

def test_buscar_pasajeros_filtros(client, db):
    cat_id = crear_categoria(db)
    pid1 = crear_persona(db, nombre="Luis")
    pid2 = crear_persona(db, nombre="Rosa")
    crear_pasajero(db, pid1, tipo_documento="DNI", numero_documento="11111111", id_categoria=cat_id)
    crear_pasajero(db, pid2, tipo_documento="Pasaporte", numero_documento="XY9999999", id_categoria=cat_id)

    resp = client.get("/pasajeros", params={"tipo_documento": "DNI"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["tipo_documento"] == "DNI"


def test_buscar_pasajeros_sin_filtros(client, db):
    cat_id = crear_categoria(db)
    pid1 = crear_persona(db)
    pid2 = crear_persona(db)
    crear_pasajero(db, pid1, id_categoria=cat_id)
    crear_pasajero(db, pid2, id_categoria=cat_id)

    resp = client.get("/pasajeros")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
