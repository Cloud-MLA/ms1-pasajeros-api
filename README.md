# MS1 — Pasajeros / Tickets

Microservicio de gestión de pasajeros, tickets, check-in y equipaje del
Aeropuerto Internacional Jorge Chávez. Python 3.12 + FastAPI + MySQL 8.

Parte del proyecto CS2032 — Cloud Computing (2026-2).

## Arquitectura

- **Puerto interno 8001** (nginx → `/api/pasajeros/*`)
- 6 tablas: `persona`, `categoria_migratoria`, `pasajero`, `ticket`, `checkin`, `equipaje`
- Consume a **MS2** vía REST para validar `id_vuelo` antes de crear tickets y equipajes

```
MS1 (pasajeros, :8001) → POST /tickets → GET {MS2}/api/vuelos/{id}/exists → MS2 (:8002)
```

## Prerrequisitos

- Docker + Docker Compose

## Levantar local

```bash
# 1. Copiar entorno
cp .env.example .env

# 2. Base de datos
docker compose up -d db

# 3. Migraciones (necesita Python local para Alembic)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DB_HOST=localhost DB_PORT=3306 DB_USER=pasajeros_user DB_PASSWORD=pasajeros_pass DB_NAME=pasajeros_db
alembic upgrade head

# 4. App
docker compose up -d --build app

# Verificar
curl http://localhost:8001/health
curl http://localhost:8001/docs
```

## Seed de desarrollo (opcional)

```bash
python -m app.scripts.seed_local   # 3 categorías + ~5k pasajeros
```

> Solo para dev/testing. Seeds de 20k para Hito 2 usan el generador
> compartido (`aeropuerto-data-science/seeds/`).

## Tests

```bash
DB_HOST=localhost DB_PORT=3306 DB_USER=test DB_PASSWORD=test DB_NAME=test \
  python -m pytest tests/ -v    # 32 tests, SQLite in-memory, sin MySQL
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/health/db` | Conexión a MySQL |
| GET | `/categorias-migratorias` | Nacional / Internacional / Tránsito + tarifa TUUA |
| POST | `/pasajeros` | Crea persona+pasajero; 409 si doc duplicado |
| GET | `/pasajeros` | Lista; filtra por `tipo_documento` + `numero_documento` |
| GET | `/pasajeros/{id}` | Devuelve pasajero; 404 si no existe |
| GET | `/pasajeros/{id}/tickets` | Tickets del pasajero |
| POST | `/tickets` | Emite ticket (valida vuelo contra MS2) |
| GET | `/tickets` | Lista; filtra por `vuelo_id` |
| GET | `/tickets/{id}` | Devuelve ticket; 404 si no existe |
| POST | `/tickets/{id}/checkin` | Check-in 1:1; segundo → 409 |
| POST | `/equipajes` | Crea equipaje (tag único, valida vuelo vs MS2) |
| GET | `/equipajes` | Lista; filtra por `pasajero_id` / `vuelo_id` |

### Formato de errores

```json
{"error": {"code": "VUELO_NO_EXISTE", "message": "El vuelo 123 no existe en MS2"}}
```

Códigos: 400 validación · 404 no encontrado · 409 duplicado · 422 precondición
(categoría/persona/vuelo inexistente o cancelado) · 502 MS2 no disponible.

## Imagen GHCR

```bash
git tag v1.0 && git push origin v1.0
# → ghcr.io/cloud-mla/ms1-pasajeros-api:v1.0 (BE-TX-05)
```

## Referencias

- [Contrato API](docs/contratos/openapi.yaml) · [Guía completa](AGENTS.md)
- E/R de la BD: `docs/er/ms1-mysql-er.*`
- Evidencias: `docs/evidencias/backend/`
