"""Tests para los endpoints de health."""
from tests.conftest import client


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "ms1-pasajeros"


def test_health_db_ok(client):
    resp = client.get("/health/db")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
