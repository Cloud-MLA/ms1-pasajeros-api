"""
Smoke test MS1 — valida la secuencia completa contra localhost:8001.

Uso:
    python -m app.scripts.smoke_test_ms1 [base_url]

Base por defecto: http://localhost:8001
Guarda la salida en docs/evidencias/backend/smoke_test.txt si existe la carpeta.
"""

import json
import sys
import time
from datetime import date

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
DOC_HAPPY = f"7{str(int(time.time()))[-7:]}"
DOC_INVALID = f"8{str(int(time.time() * 10))[-7:]}"
TAG_BASE = "TAg" + str(int(time.time() * 1000))[-10:]


def req(method: str, path: str, **kw):
    return httpx.request(method, f"{BASE}{path}", timeout=10.0, **kw)


def show(label: str, resp: httpx.Response):
    print(f"\n### {label}")
    print(f"  {resp.request.method} {resp.request.url} -> {resp.status_code}")
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    print("  " + json.dumps(body, ensure_ascii=False, indent=2))


def main():
    ok = True

    r = req("GET", "/health")
    show("health", r)
    ok &= r.status_code == 200

    r = req("GET", "/health/db")
    show("health/db", r)
    ok &= r.status_code == 200

    r = req("GET", "/categorias-migratorias")
    show("categorias-migratorias", r)
    ok &= r.status_code == 200

    # Buscar un id de vuelo que NO este cancelado en el mock MS2
    ok_id = cancel_id = None
    for vid in range(1, 500):
        rv = req("GET", f"/ms2/vuelos/{vid}/exists")
        if rv.status_code != 200:
            continue
        data = rv.json()
        if data.get("estado") != "Cancelado" and ok_id is None:
            ok_id = vid
        elif data.get("estado") == "Cancelado" and cancel_id is None:
            cancel_id = vid
        if ok_id and cancel_id:
            break
    print(f"\n# Mock MS2 -> vuelo valido: {ok_id}; vuelo cancelado: {cancel_id}")

    r = req("POST", "/pasajeros", json={
        "nombre": "Juan", "apellido": "Perez",
        "fecha_nacimiento": "1992-04-11",
        "tipo_documento": "DNI", "numero_documento": DOC_HAPPY,
        "id_categoria": 1,
    })
    show("POST /pasajeros", r)
    ok &= r.status_code == 201
    id_persona = r.json()["id_persona"]

    r = req("POST", "/pasajeros", json={
        "nombre": "Juan", "apellido": "Perez",
        "fecha_nacimiento": "1992-04-11",
        "tipo_documento": "DNI", "numero_documento": DOC_HAPPY,
        "id_categoria": 1,
    })
    show("POST /pasajeros (duplicado -> 409)", r)
    ok &= r.status_code == 409

    r = req("POST", "/pasajeros", json={
        "nombre": "Ana", "apellido": "Lopez",
        "fecha_nacimiento": "1990-01-01",
        "tipo_documento": "DNI", "numero_documento": DOC_INVALID,
        "id_categoria": 99,
    })
    show("POST /pasajeros (categoria invalida -> 422)", r)
    ok &= r.status_code == 422

    r = req("GET", f"/pasajeros/{id_persona}")
    show(f"GET /pasajeros/{id_persona}", r)
    ok &= r.status_code == 200

    r = req("GET", "/pasajeros?tipo_documento=DNI&numero_documento=" + DOC_HAPPY)
    show("GET /pasajeros?tipo_documento=&numero_documento=", r)
    ok &= r.status_code == 200

    r = req("POST", "/tickets", json={
        "precio": 185.00, "fecha_emision": date.today().isoformat(),
        "id_vuelo": ok_id, "id_persona": id_persona,
    })
    show(f"POST /tickets (vuelo ok {ok_id})", r)
    ok &= r.status_code == 201
    id_ticket = r.json()["id_ticket"]

    r = req("POST", "/tickets", json={
        "precio": 185.00, "fecha_emision": date.today().isoformat(),
        "id_vuelo": cancel_id, "id_persona": id_persona,
    })
    show(f"POST /tickets (vuelo cancelado -> 422 {cancel_id})", r)
    ok &= r.status_code == 422

    r = req("POST", "/tickets", json={
        "precio": 185.00, "fecha_emision": date.today().isoformat(),
        "id_vuelo": 99999, "id_persona": id_persona,
    })
    show("POST /tickets (vuelo inexistente -> 422)", r)
    ok &= r.status_code == 422

    r = req("GET", f"/tickets/{id_ticket}")
    show(f"GET /tickets/{id_ticket}", r)
    ok &= r.status_code == 200

    r = req("GET", f"/tickets?vuelo_id={ok_id}")
    show(f"GET /tickets?vuelo_id={ok_id}", r)
    ok &= r.status_code == 200

    r = req("GET", f"/pasajeros/{id_persona}/tickets")
    show(f"GET /pasajeros/{id_persona}/tickets", r)
    ok &= r.status_code == 200

    r = req("POST", f"/tickets/{id_ticket}/checkin", json={})
    show(f"POST /tickets/{id_ticket}/checkin", r)
    ok &= r.status_code == 201

    r = req("POST", f"/tickets/{id_ticket}/checkin", json={"counter": "C1"})
    show(f"POST /tickets/{id_ticket}/checkin (2do -> 409)", r)
    ok &= r.status_code == 409

    r = req("GET", f"/tickets/999999")
    show("GET /tickets/999999 (no existe -> 404)", r)
    ok &= r.status_code == 404

    r = req("POST", "/equipajes", json={
        "id": TAG_BASE + "1", "peso": 15.40,
        "id_persona": id_persona, "id_vuelo": ok_id,
    })
    show(f"POST /equipajes (vuelo ok {ok_id})", r)
    ok &= r.status_code == 201

    r = req("POST", "/equipajes", json={
        "id": TAG_BASE + "2", "peso": 10.00,
        "id_persona": id_persona, "id_vuelo": 99999,
    })
    show("POST /equipajes (vuelo inexistente -> 422)", r)
    ok &= r.status_code == 422

    r = req("GET", f"/equipajes?pasajero_id={id_persona}")
    show(f"GET /equipajes?pasajero_id={id_persona}", r)
    ok &= r.status_code == 200

    r = req("GET", f"/equipajes?vuelo_id={ok_id}")
    show(f"GET /equipajes?vuelo_id={ok_id}", r)
    ok &= r.status_code == 200

    print("\n==============================")
    print("RESULTADO:", "OK" if ok else "FALLO")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()