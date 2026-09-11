"""Tests para los endpoints de tickets (POST, GET, búsqueda)."""
from unittest.mock import patch

from tests.conftest import (
    client, db, crear_categoria, crear_persona, crear_pasajero, crear_ticket,
    mock_vuelo_exists_ok, mock_vuelo_exists_cancelado,
)


# ===================== POST /tickets =====================

@patch("app.services.ticket_service.httpx.get")
def test_crear_ticket_ok(mock_get, client, db):
    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_ok(1)

    payload = {
        "precio": 250.00,
        "fecha_emision": "2026-09-10",
        "id_vuelo": 1,
        "id_persona": pid,
    }
    resp = client.post("/tickets", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["precio"] == 250.0
    assert data["estado_boarding"] == "Emitido"
    assert "id_ticket" in data


@patch("app.services.ticket_service.httpx.get")
def test_crear_ticket_vuelo_cancelado(mock_get, client, db):
    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_cancelado(999)

    payload = {
        "precio": 100.00,
        "fecha_emision": "2026-09-10",
        "id_vuelo": 999,
        "id_persona": pid,
    }
    resp = client.post("/tickets", json=payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VUELO_CANCELADO"


@patch("app.services.ticket_service.httpx.get")
def test_crear_ticket_vuelo_no_existe(mock_get, client, db):
    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)

    mock_get.return_value.status_code = 404

    payload = {
        "precio": 100.00,
        "fecha_emision": "2026-09-10",
        "id_vuelo": 30000,
        "id_persona": pid,
    }
    resp = client.post("/tickets", json=payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VUELO_NO_EXISTE"


def test_crear_ticket_persona_no_existe(client, db):
    payload = {
        "precio": 100.00,
        "fecha_emision": "2026-09-10",
        "id_vuelo": 1,
        "id_persona": 99999,
    }
    resp = client.post("/tickets", json=payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "PERSONA_NO_EXISTE"


# ===================== GET /tickets/{id} =====================

def test_obtener_ticket_ok(client, db):
    pid = crear_persona(db)
    tid = crear_ticket(db, id_persona=pid, precio=300.00)

    resp = client.get(f"/tickets/{tid}")
    assert resp.status_code == 200
    assert resp.json()["id_ticket"] == tid
    assert resp.json()["precio"] == 300.0


def test_obtener_ticket_no_existe(client):
    resp = client.get("/tickets/99999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NO_ENCONTRADO"


# ===================== GET /tickets?vuelo_id= =====================

def test_buscar_tickets_por_vuelo(client, db):
    pid = crear_persona(db)
    crear_ticket(db, id_vuelo=1, id_persona=pid)
    crear_ticket(db, id_vuelo=1, id_persona=pid)
    crear_ticket(db, id_vuelo=2, id_persona=pid)

    resp = client.get("/tickets", params={"vuelo_id": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_buscar_tickets_sin_filtro(client, db):
    pid = crear_persona(db)
    crear_ticket(db, id_persona=pid)
    crear_ticket(db, id_persona=pid)

    resp = client.get("/tickets")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ===================== GET /pasajeros/{id}/tickets =====================

def test_tickets_de_pasajero(client, db):
    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)
    crear_ticket(db, id_persona=pid)
    crear_ticket(db, id_persona=pid)

    resp = client.get(f"/pasajeros/{pid}/tickets")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_tickets_de_pasajero_no_existe(client):
    resp = client.get("/pasajeros/99999/tickets")
    assert resp.status_code == 404
