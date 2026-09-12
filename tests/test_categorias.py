"""Tests para GET /categorias-migratorias."""
from tests.conftest import client, db, crear_categoria


def test_listar_categorias_vacio(client):
    resp = client.get("/categorias-migratorias")
    assert resp.status_code == 200
    assert resp.json() == []


def test_listar_categorias(client, db):
    crear_categoria(db, "Nacional", 12.50)
    crear_categoria(db, "Internacional", 38.45)
    crear_categoria(db, "Transito", 18.00)

    resp = client.get("/categorias-migratorias")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    nombres = {c["nombre"] for c in data}
    assert nombres == {"Nacional", "Internacional", "Transito"}
