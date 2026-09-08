# ms1-pasajeros-api
MS1 — Pasajeros / Tickets · Python + FastAPI + MySQL 8

Parte del Proyecto Parcial CS2032 — Cloud Computing (2026-2).
Contexto y arquitectura: [`cloud-computing-proyecto`](https://github.com/btoroled/cloud-computing-proyecto) ·
Plan de tareas: [`plan/backend.md` §4](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/plan/backend.md) ·
Dueño: Guillermo.

## Puesta en marcha (base desde la plantilla · BE-TX-02)

Este repo trae ya los archivos comunes: `.editorconfig`, `.gitignore`, `.env.example`,
`.github/workflows/build-push-ghcr.yml`. Fuente: [plantilla común](https://github.com/Cloud-MLA/aeropuerto-infra-deploy/tree/main/plantilla).

**Pendiente de scaffold (MS1-01, Guillermo):**
- Copiar `plantilla/docker/Dockerfile.python` como `Dockerfile` y ajustar el entrypoint (`app.main:app`).
- `docker-compose.yml` local: app + `mysql:8`.
- `GET /health` y `GET /docs` (Swagger-UI).
- `openapi.yaml` borrador (BE-TX-03).

## Convenciones

- **Puerto interno:** `8001` (lo espera el nginx de producción).
- **Errores:** [contrato común](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/contratos/errores.md).
- **Enums y rangos de ID:** [diccionario compartido](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/contratos/enums.md)
  (`persona.id` / `pasajero.id` 100 000–160 000 · `ticket.id` 1–60 000).
- **Imagen:** `git tag vX.Y && git push --tags` → `ghcr.io/cloud-mla/ms1-pasajeros-api:vX.Y`.

## Endpoints (previstos)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/docs` | Swagger-UI |
| CRUD | `/pasajeros` | Pasajeros (búsqueda por `tipo_documento`+`numero_documento`) |
| GET | `/categorias-migratorias` | Nacional / Internacional / Transito + tarifa TUUA |
| POST | `/tickets` | Emite ticket (valida vuelo contra MS2) |
| GET | `/tickets/{id}`, `/tickets?vuelo_id=`, `/pasajeros/{id}/tickets` | Consultas |
| POST | `/tickets/{id}/checkin` | Check-in (1:1 con ticket) |
| POST/GET | `/equipajes` | Equipaje por pasajero / vuelo |
