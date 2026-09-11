"""Tests para los endpoints de equipajes (POST, GET con filtros)."""
from unittest.mock import patch

from tests.conftest import (
    client, db, crear_categoria, crear_persona, crear_pasajero,
    mock_vuelo_exists_ok, mock_vuelo_exists_cancelado,
)


# ===================== POST /equipajes =====================

@patch("app.services.ticket_service.httpx.get")
def test_crear_equipaje_ok(mock_get, client, db):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_ok(1)
    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)

    payload = {
        "id": "BHS000000001",
        "peso": 18.5,
        "id_persona": pid,
        "id_vuelo": 1,
    }
    resp = client.post("/equipajes", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == "BHS000000001"
    assert data["peso"] == 18.5


@patch("app.services.ticket_service.httpx.get")
def test_crear_equipaje_tag_duplicado(mock_get, client, db):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_ok(1)
    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)

    payload = {
        "id": "BHS000000001",
        "peso": 10.0,
        "id_persona": pid,
        "id_vuelo": 1,
    }
    resp1 = client.post("/equipajes", json=payload)
    assert resp1.status_code == 201

    payload2 = payload.copy()
    payload2["peso"] = 20.0
    resp2 = client.post("/equipajes", json=payload2)
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "DUPLICADO"


@patch("app.services.ticket_service.httpx.get")
def test_crear_equipaje_persona_no_existe(mock_get, client, db):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_ok(1)
    payload = {
        "id": "BHS000000001",
        "peso": 15.0,
        "id_persona": 99999,
        "id_vuelo": 1,
    }
    resp = client.post("/equipajes", json=payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "PERSONA_NO_EXISTE"


@patch("app.services.ticket_service.httpx.get")
def test_crear_equipaje_vuelo_cancelado(mock_get, client, db):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_cancelado(999)

    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)

    payload = {
        "id": "BHS000000001",
        "peso": 10.0,
        "id_persona": pid,
        "id_vuelo": 999,
    }
    resp = client.post("/equipajes", json=payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VUELO_CANCELADO"


# ===================== GET /equipajes?pasajero_id=&vuelo_id= =====================

@patch("app.services.ticket_service.httpx.get")
def test_buscar_equipajes_por_pasajero(mock_get, client, db):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_ok(1)
    cat_id = crear_categoria(db)
    pid1 = crear_persona(db)
    pid2 = crear_persona(db)
    crear_pasajero(db, pid1, id_categoria=cat_id)
    crear_pasajero(db, pid2, id_categoria=cat_id)

    client.post("/equipajes", json={"id": "BHS000000001", "peso": 10.0, "id_persona": pid1, "id_vuelo": 1})
    client.post("/equipajes", json={"id": "BHS000000002", "peso": 15.0, "id_persona": pid2, "id_vuelo": 1})

    resp = client.get("/equipajes", params={"pasajero_id": pid1})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id_persona"] == pid1


@patch("app.services.ticket_service.httpx.get")
def test_buscar_equipajes_por_vuelo(mock_get, client, db):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_vuelo_exists_ok(1)
    cat_id = crear_categoria(db)
    pid = crear_persona(db)
    crear_pasajero(db, pid, id_categoria=cat_id)

    client.post("/equipajes", json={"id": "BHS000000001", "peso": 10.0, "id_persona": pid, "id_vuelo": 1})
    client.post("/equipajes", json={"id": "BHS000000002", "peso": 12.0, "id_persona": pid, "id_vuelo": 2})

    resp = client.get("/equipajes", params={"vuelo_id": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id_vuelo"] == 1
