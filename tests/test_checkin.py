"""Tests para POST /tickets/{id}/checkin."""
from tests.conftest import client, db, crear_ticket


def test_checkin_ok(client, db):
    tid = crear_ticket(db)
    resp = client.post(f"/tickets/{tid}/checkin", json={"counter": "C01", "con_equipaje": True})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id_ticket"] == tid
    assert data["counter"] == "C01"
    assert data["con_equipaje"] is True
    assert "fecha_hora" in data


def test_checkin_sin_body(client, db):
    tid = crear_ticket(db)
    resp = client.post(f"/tickets/{tid}/checkin")
    assert resp.status_code == 201
    data = resp.json()
    assert data["con_equipaje"] is False
    assert data["counter"] is None


def test_checkin_ticket_no_existe(client):
    resp = client.post("/tickets/99999/checkin")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NO_ENCONTRADO"


def test_checkin_duplicado(client, db):
    tid = crear_ticket(db)
    resp1 = client.post(f"/tickets/{tid}/checkin")
    assert resp1.status_code == 201

    resp2 = client.post(f"/tickets/{tid}/checkin")
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "DUPLICADO"
