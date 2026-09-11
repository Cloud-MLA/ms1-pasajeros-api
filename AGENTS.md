# AGENTS.md — Guía del Dev A (MS1)

Contexto rápido para trabajar como **Dev A** en el proyecto **CS2032 — Cloud Computing (2026-2)**
(Aeropuerto Internacional Jorge Chávez). Resumen de lo que hay en `docs/` listo para actuar hasta
**F1 completa + integración MS1→MS2 (revisión 11-Set)**, sin volver a leer todo el repo.

---

## 1. Rol y entregables del Dev A

- Repo de código que lidero: **`ms1-pasajeros-api`** (aún `_pendiente_` en `INDEX.md`).
- Stack: **Python + FastAPI + MySQL 8**.
- También soy responsable del contenedor **`ingesta-ms1`** (en `aeropuerto-data-science`): lee la BD
  MySQL → CSV → S3 (`raw/ms1/`).
- Documentación que mantengo en este repo: `docs/er/ms1-mysql-er.*` (E/R de MySQL), evidencias en
  `docs/evidencias/backend/`, y mi sección del informe.

## 2. Fechas clave

| Hito | Fecha | Qué necesito |
|---|---|---|
| Hito 1 (ACL) | Sáb **12-Set** 23:59 | MS1 con CRUD mínimo + MS1→MS2 + BD MySQL conectada + `ingesta-ms1` cargando a S3 (seed ~5k) |
| Hito 2 (Canvas) | Dom **20-Set** 23:59 | MS1 completo + **20k** en `ticket`/`equipaje` + Swagger + E/R MySQL |
| Exposición presencial | Semana 7 | obligatoria |

Fases: **F0** = Mié 2 – Vie 4 · **F1** = Sáb 6 – Sáb 12 · **F2** = Sáb 13 – Vie 19.

**Hoy: Vie 11-Set 2026** — Hito 1 mañana; F2 arrancado.

## 3. La BD de MS1 (`pasajeros_db`)

**6 tablas** en MySQL 8. Solo habrá **FK físicas internas**; `ticket.id_vuelo` y `equipaje.id_vuelo`
son **referencias suaves** a MS2 (no FK), validadas por REST.

| Tabla | PK | Atributos | Reglas |
|---|---|---|---|
| `persona` | `id_persona` INT AUTO | `nombre` VARCHAR(50) NOT NULL, `apellido` VARCHAR(50) NOT NULL, `fecha_nacimiento` DATE NOT NULL | superclase identidad |
| `categoria_migratoria` | `id` INT AUTO | `nombre` ENUM(`Nacional`,`Internacional`,`Transito`) NOT NULL, `tarifa` DECIMAL(10,2) NOT NULL | CHECK(`tarifa>=0`) |
| `pasajero` | `id_persona` FK→persona | `tipo_documento` ENUM(`DNI`,`Pasaporte`,`Carnet de Extranjeria`) NOT NULL, `numero_documento` VARCHAR(15) NOT NULL, `id_categoria` FK→categoria | **UNIQUE**(`tipo_documento`,`numero_documento`) |
| `ticket` | `id_ticket` BIGINT AUTO | `precio` NUMERIC(10,2) NOT NULL, `fecha_emision` DATE NOT NULL, `estado_boarding` ENUM(`Emitido`,`Check-in`,`Embarcado`,`No-show`,`Cancelado`) DEFAULT `Emitido`, `id_vuelo` soft→MS2, `id_persona` FK→persona | volumen ≥20k |
| `checkin` | `id_ticket` FK→ticket | `fecha_hora` TIMESTAMP NOT NULL, `counter` VARCHAR(10), `con_equipaje` BOOLEAN DEFAULT FALSE | entidad débil, 1:1 con ticket, `ON DELETE CASCADE` |
| `equipaje` | `id` VARCHAR(20) (=Tag ID) | `peso` NUMERIC(6,2) NOT NULL, `id_persona` FK→persona, `id_vuelo` soft→MS2 | CHECK(`peso>0`); volumen ≥20k |

Relaciones: persona 1–1 pasajero (IsA) · categoria 1–N pasajero · persona 1–N ticket · ticket 1–1
checkin · pasajero 1–N equipaje.

**Rangos de ID (no negociables, plan-de-trabajo §3):**
`persona.id` ∈ **100 000 – 160 000** · `ticket.id` ∈ **1 – 60 000**. Los `id_vuelo` que cree MS2 viven en
[1 – 25 000]. Orden de generación de data: **MS2 → MS1 → MS3** (por eso los vuelos ya existen).

## 4. Enums que DEBO respetar (contratos/enums.md — strings idénticos, sin acentos)

- `tipo_documento`: `DNI` · `Pasaporte` · `Carnet de Extranjeria`
- `estado_boarding`: `Emitido` · `Check-in` · `Embarcado` · `No-show` · `Cancelado`
- `nombre_categoria_migratoria`: `Nacional` · `Internacional` · `Transito`

Importante: **sin tildes** en los enums (`Transito` no lleva tilde). Fechas en **ISO 8601 UTC**
(`2026-09-02T14:22:00Z`). Montos en **soles (PEN)**, decimal con punto, 2 decimales.
Cambiar un enum rompe a MS2/MS3 y los joins de Athena → solo por PR + aviso en standup.

## 5. API de MS1 (base `/api/pasajeros`, nginx → puerto 8001)

Cada servicio expone `GET /health`, `GET /openapi.json` y Swagger-UI en `/docs`.

### F0
- **MS1-01** Scaffold FastAPI + `Dockerfile` + `compose` local (app + `mysql:8`) → `GET /health` OK.
- **MS1-02** Migraciones de las 6 tablas (modelo de §3) → E/R a `docs/er/ms1-mysql-er.*`.
- **BE-TX-03** `openapi.yaml` borrador (contract-first), revisado en standup Día 2.
- Salida F0: `GET /health` + 1 endpoint real + `openapi.yaml`.

### F1
- **MS1-03** `POST /pasajeros` (crea `persona`+`pasajero`; 409 si `tipo_documento`+`numero_documento`
  ya existe) · `GET /pasajeros/{id}` · `GET /pasajeros?tipo_documento=&numero_documento=`. Seed ~5k.
- **MS1-04** `GET /categorias-migratorias` (las 3 categorías con tarifa TUUA).
- **MS1-05** `POST /tickets` — **valida vuelo contra MS2** (`GET /vuelos/{id}/exists`); si no existe o
  `Cancelado` → **422**; log de llamada saliente. ← tarea clave (consume a otro MS).
- **MS1-06** `GET /tickets/{id}` · `GET /tickets?vuelo_id=` · `GET /pasajeros/{id}/tickets`.
- **MS1-07** `POST /tickets/{id}/checkin` (1:1; 2º check-in del mismo ticket → **409**).
- **MS1-08** `POST /equipajes` + `GET /equipajes?pasajero_id=` / `?vuelo_id=`.
- **DS-06 / ingesta-ms1** contenedor Python: `SELECT *` 100% de las 6 tablas → CSV →
  `raw/ms1/<tabla>/<fecha>/` en S3.
- Salida Hito 1: CRUD mínimo + MS1→MS2 + BD conectada + `ingesta-ms1` cargando a S3.

### F2 (resumen, para después)
- Carga masiva ≥**20 000** en `ticket` y `equipaje` (una vez), `COUNT(*)` como evidencia.
- Swagger completo + pruebas (happy path + validación de error).
- README (levantar local / tras corte) + tag `v1.0` → imagen GHCR.

## 6. Decisiones ya tomadas (para no repetir investigación)

- **Motor = MySQL 8.** Se descartó MariaDB: el enunciado nombra explícitamente "MySQL" y todo el repo
  asume `mysql:8` (`INDEX.md`, `arquitectura.md:33`, `backend.md`, `verificacion.md`, `er/README.md`,
  `data-science.md`). Código casi idéntico, pero cambia a mejor contratos y docs.
- **Enums en DB:** MySQL usa `ENUM` / `CHECK` (los `JOIN` de Athena dependen de los strings).
- **Soft refs a MS2** (`id_vuelo`) sin FK física — validación por REST, materializa "MS consume a MS".
- **Dependencia bloqueante MS2-07 resuelta (11-Set):** `GET /api/vuelos/{id}/exists` ya está real en
  `ms2-vuelos-api` (ver contrato abajo). El **gap actual es el seed de vuelos de MS2**: sin vuelos
  cargados, `/exists` → 404 (en MS1: 422 `VUELO_NO_EXISTE`). Seed = tarea de Dev B (Hito 1 ~2–5k;
  MS2-09 20k en F2). Mientras no haya vuelos, el mock interno sigue como fallback de dev.
- **Contrato de errores común (BE-TX-08):** formato JSON de error uniforme, códigos 400/404/409/422/502.
- **Cliente HTTP compartido (BE-TX-09):** timeout, reintento, propagación de error (Variable).
- **ORM = SQLAlchemy 2 + Alembic** para migraciones (decisión tomada; ningún otro ORM).
- **Credenciales en `.env`** (nunca hardcodeadas); se ignora en git vía `.gitignore`.
- **Hosts distintos según dónde se corre:** dentro de Docker, `DB_HOST=db` (nombre del servicio del
  compose); **en local (fuera de Docker), Alembic/dev necesita `DB_HOST=localhost`** — el puerto 3306
  está publicado por el compose.
- **MS2 real ya existe (11-Set):** `ms2-vuelos-api` (Spring Boot + PostgreSQL 16, puerto 8002) con
  `GET /api/vuelos/{id}/exists` implementado y CI GHCR. El **mock local** (`/ms2/vuelos/*`) queda solo
  como fallback de dev si MS2 está caído.
- **E/R lo dibuja el Lead/Dev A a mano** en `docs/er/` — el repo de código no exporta el diagrama.
- **Tarifas TUUA (provisionales):** Nacional 12.50 · Internacional 38.45 · Transito 18.00 (PEN).
  Marcadas como **provisionales** hasta confirmación del equipo; seed y openapi.yaml usan estos valores.
- **Contrato MS2-07 verificado en código real (11-Set):** `GET /api/vuelos/{id}/exists` (Spring Boot,
  base `/api/vuelos`) → 200 `{exists, estado}` / 404. Enum `estado_vuelo` correcto: `Programado ·
  Embarcando · Despegado · Aterrizado · Retrasado · Cancelado` (coincide con enums.md). Mock local en
  `GET /ms2/vuelos/{id}/exists` (solo fallback de dev).
- **URL de MS2 por variable de entorno:** `MS2_BASE_URL` (default `http://localhost:8002`). El código
  construye `{MS2_BASE_URL}/api/vuelos/{id}/exists`. Switch a MS2 real es **solo cambiar la variable**.
  Demo local 1 máquina: `MS2_BASE_URL=http://host.docker.internal:8002` + `extra_hosts:
  ["host.docker.internal:host-gateway"]` en el servicio `app` del compose. En prod (nginx):
  `http://<nginx>/api/vuelos`. Documentada en `.env.example`.
- **Formato ingesta S3 (DS-06):** `raw/ms1/<tabla>/<fecha>/` (6 tablas, CSV, 100% pull).
  Depende de bucket S3 creado por Lead (DS-04) y VM-INGESTA (DS-05).
- **Seed reproducible:** `SEED` fijo para data ficticia; ~5k pasajeros en rango 100k–160k.
- **Repo sin git:** por decisión del usuario, no se inicializa git en este repo (commits vía PR en docs/).

### Decisiones resueltas (F1)

- **Seed local para dev/testing:** creación de `app/scripts/seed_local.py` que inserta 3 categorías +
  ~5k pasajeros (rango 100k–160k) en la DB local. **Solo para desarrollo y testing de endpoints;**
  no reemplaza al `seeds/` compartido de Dev D (`aeropuerto-data-science/seeds/`, DS-02) que genera
  CSVs para data Science. Ejecutar con `python -m app.scripts.seed_local`.
- **openapi.yaml - corrección aplicada:** el enum `estado_vuelo` del mock en `docs/contratos/openapi.yaml`
  fue corregido a: `Programado · Embarcando · Despegado · Aterrizado · Retrasado · Cancelado`
  (según `docs/contratos/enums.md` canonical). Corregido en F1.16.
- **ingesta-ms1 (DS-06):** contenedor Python que vive en `aeropuerto-data-science/`. Yo escribo el
  código: conexión MySQL → `SELECT *` 6 tablas → CSV → `put_object` a `raw/ms1/<tabla>/<fecha>/` en S3.
  Para F1 preparo el script; integro cuando DS-04 (bucket) + DS-05 (VM-INGESTA) estén listos.
- **Equipaje también valida vuelo contra MS2 (canon `requerimientos.md` §3.2):** las referencias suaves
  (`ticket.vuelo_id`, `equipaje.vuelo_id`) "se validan con una llamada REST al escribir". `POST /equipajes`
  reusa `validar_vuelo` → vuelo inexistente/cancelado = 422. Aplicado en la revisión F1.20.
- **Check-in NO cambia `estado_boarding`:** el canon (§4.1) solo pide registrar el check-in 1:1. Los
  estados `Check-in`/`Embarcado` que necesita Q4 de Athena (filtra esos estados) se setean en la carga
  masiva 20k (F2), no en el endpoint. Decisión tomada en la revisión (E9).

### Decisiones de integración (11-Set, alineadas al canon `docs/plan/backend.md`)

- **Demo/entrega local = 1 máquina** (decisión del usuario): los 3 MS corren en composes locales con
  puertos distintos por host — MS1 `8001`, MS2 `8002`, MS3 `3003` — y se interconectan vía
  `host.docker.internal` (en Linux: `extra_hosts: ["host.docker.internal:host-gateway"]`).
- **Tag de imagen final = GHCR (canon BE-TX-05):** `ghcr.io/cloud-mla/ms1-pasajeros-api:v1.0`. Debo
  agregar `.github/workflows/build-push-ghcr.yml` a este repo (hoy no existe; MS2 ya lo tiene).
- **Seeds de 20k (F2):** usar el **generador compartido de Dev D** (`aeropuerto-data-science/seeds/`,
  DS-02), **no** mini-seeds ad-hoc. Orden MS2 → MS1 → MS3. `seed_local.py` sigue siendo solo dev/testing.
- **Hito 1 (Sáb 12):** seeds ~2–5k; los 20k pertenecen a Hito 2. MS1 con su seed 5k ya cumple; MS2
  necesita seed de vuelos de Dev B para que el happy path de `POST /tickets` funcione contra MS2 real.

## 7. Convenciones de este repo de documentación

- Ramas `docs/<tema>` + PR con 1 revisión (normalmente el Lead); **no** commiteo directo a `main`.
- Español, Markdown, líneas ≤ ~100 caracteres, tablas para listas de tareas/datos.
- Avisar en el standup cualquier cambio de enum/endpoint compartido (rompe a otros).

## 8. Plan de ejecución para mí (Dev A / modelo), en orden, hasta completar F0 y F1

Checklist numerado de trabajos pequeños. Verifico cada uno con su DoD antes de pasar al siguiente.
Al terminar cada tarea marco la casilla `[x]`.

### F0 — Setup y contratos (Mié 2 – Vie 4)
Objetivo de salida: `GET /health` + 1 endpoint real + `openapi.yaml`.

- [x] **1.** Crear/estructurar el repo `ms1-pasajeros-api` desde la plantilla (README, `.editorconfig`,
      `.env.example`, `LICENSE`, `.gitignore`). *(Depende de BE-TX-02.)*
- [x] **2.** Revisar `docs/contratos/enums.md` + rangos de ID (plan-de-trabajo §3) y confirmar que el
      modelo de §3 de este AGENTS encaja. *(BE-TX-01.)*
- [x] **3.** Scaffold FastAPI: `app/` con `main.py`, `/health`, config por entorno, `Dockerfile`
      (py:3.12-slim) + `docker-compose.yml` local (app + `mysql:8`). → **MS1-01**: `GET /health` OK.
      *(Verificado: `/health` y `/health/db` responden 200 desde el contenedor.)*
- [x] **4.** Escribir DDL de migración de las **6 tablas** (modelo de §3): `persona`, `categoria_migratoria`,
      `pasajero` (UNIQUE doc), `ticket`, `checkin` (débil, CASCADE), `equipaje`. Aplicar en el compose
      local. → **MS1-02**: migración aplica. *(Ojo: Alembic local usa `DB_HOST=localhost`.)*
- [x] ~~**5.** Exportar el **E/R**~~ → lo dibuja el Lead/Dev A a mano; el repo no exporta el diagrama.
- [x] **6.** Redactar `openapi.yaml` borrador (contract-first) con los endpoints de §5 y validarlo.
      → **BE-TX-03**, revisado en el standup Día 2. *(En `docs/contratos/openapi.yaml`.)*
- [x] **7.** (Contingencia) Contrato MS2-07 documentado en openapi.yaml; mock funcional en F1.

### F1 — Núcleo + MS1→MS2 + ingesta (Sáb 6 – Sáb 12 → Hito 1)
Objetivo de salida: CRUD mínimo + MS1→MS2 + BD conectada + `ingesta-ms1` en S3.

*Estrategia: **un endpoint por paso**, permiso antes de cada uno.*

| # | Tarea | Endpoint(s) | Archivos a crear/modificar | DoD |
|---|---|---|---|---|
| **F1.1** | Schemas Pydantic + formato error | — | `app/schemas/` (pasajero, ticket, checkin, equipaje, error) | Todos los schemas listos; formato `ErrorBody` uniforme |
| **F1.2** | Seed 3 categorías + `GET /categorias-migratorias` | `GET /categorias-migratorias` | `app/routers/categorias.py`, `app/scripts/seed_local.py` (parte 1) | Las 3 categorías con tarifa se devuelven |
| **F1.3** | `POST /pasajeros` | `POST /pasajeros` | `app/routers/pasajeros.py`, `app/services/pasajero_service.py` | Crea persona+pasajero; 409 si duplicado doc |
| **F1.4** | `GET /pasajeros/{id}` | `GET /pasajeros/{id}` | `app/routers/pasajeros.py` | Devuelve pasajero; 404 si no existe |
| **F1.5** | `GET /pasajeros?tipo_documento=&numero_documento=` | `GET /pasajeros` (query) | `app/routers/pasajeros.py` | Búsqueda por tipo+num doc funciona |
| **F1.6** | Seed ~5k pasajeros (local dev/testing) | — | `app/scripts/seed_local.py` (parte 2) | ~5k registros en rango 100k–160k en DB local |
| **F1.7** | Mock MS2 `GET /ms2/vuelos/{id}/exists` | `GET /ms2/vuelos/{id}/exists` | `app/routers/mock_ms2.py` | 200 `{exists,estado}` para IDs 1–25000; 404 fuera |
| **F1.8** | `POST /tickets` (valida contra mock MS2) | `POST /tickets` | `app/routers/tickets.py`, `app/services/ticket_service.py` | Vuelo inexistente/Cancelado → 422; log saliente |
| **F1.9** | `GET /tickets/{id}` | `GET /tickets/{id}` | `app/routers/tickets.py` | Devuelve ticket; 404 si no existe |
| **F1.10** | `GET /tickets?vuelo_id=` | `GET /tickets` (query) | `app/routers/tickets.py` | Filtrado por vuelo funciona |
| **F1.11** | `GET /pasajeros/{id}/tickets` | `GET /pasajeros/{id}/tickets` | `app/routers/pasajeros.py` | Lista tickets del pasajero; 404 si pasajero no existe |
| **F1.12** | `POST /tickets/{id}/checkin` (1:1) | `POST /tickets/{id}/checkin` | `app/routers/checkin.py`, `app/services/checkin_service.py` | Check-in registrado; 2º → 409; ticket inexistente → 404 |
| **F1.13** | `POST /equipajes` | `POST /equipajes` | `app/routers/equipajes.py`, `app/services/equipaje_service.py` | Tag ID único; peso > 0; 409 duplicado tag |
| **F1.14** | `GET /equipajes?pasajero_id=&vuelo_id=` | `GET /equipajes` (query) | `app/routers/equipajes.py` | Filtrado por pasajero/vuelo funciona |
| **F1.15** | `ingesta-ms1` script | — | `app/scripts/ingesta_ms1.py` (o repo aparte) | SELECT * 6 tablas → CSV → S3 |
| **F1.16** | ~~Corregir `openapi.yaml` mock enum~~ | ~~`docs/contratos/openapi.yaml`~~ | ~~`estado_vuelo` = canonical de enums.md~~ | ✅ Hecho |
| **F1.17** | Prueba humo + evidencia | — | `docs/evidencias/backend/` | Capturas de endpoints funcionando |

**Correspondencia:** F1.2=MS1-04, F1.3–F1.6=MS1-03, F1.7–F1.8=MS1-05, F1.9–F1.11=MS1-06, F1.12=MS1-07, F1.13–F1.14=MS1-08, F1.15=DS-06, F1.17=Hito 1.

### F1.18 – F1.26 · Correcciones de consistencia (revisión código vs docs canónicos)

Detectadas el 10-Set cotejando contra `cloud-computing-proyecto` (`requerimientos.md`, `backend.md`,
`contratos/enums.md`, `data-science.md`). Se aplican en orden; cada una deja su casilla `[x]` al verificar.

| # | Tarea | Archivos | DoD |
|---|---|---|---|
| **F1.18** | `boto3` en `requirements.txt` (la ingesta lo importa) | `requirements.txt` | `ingesta_ms1.py` importa sin error |
| **F1.19** | `MS2_BASE_URL` configurable por env (default `http://localhost:8002`) | `app/config.py`, `.env.example` | Switch a MS2 real = solo variable |
| **F1.20** | Log `INFO` de la llamada saliente MS1→MS2 (vuelo id + status) y usar `settings.MS2_BASE_URL` | `app/services/ticket_service.py` | Log visible al emitir ticket; DoD MS1-05 |
| **F1.21** | `POST /equipajes` valida vuelo contra MS2 (reusa `validar_vuelo`); canon §3.2 | `app/services/equipaje_service.py` | Vuelo inexistente/cancelado → 422; alineado con openapi |
| **F1.22** | `try/except IntegrityError → 409` en `crear_pasajero` y `crear_equipaje` | `app/services/pasajero_service.py`, `equipaje_service.py` | Requests simultáneos duplicados → 409 (no 500) |
| **F1.23** | Validar `id_categoria` existente → 422 `CATEGORIA_NO_EXISTE` | `app/services/pasajero_service.py` | `id_categoria` inválido no produce 500 por FK |
| **F1.24** | `GET /pasajeros` sin N+1 (join Persona×Pasajero en una query) | `app/routers/pasajeros.py` | ~1 query para el seed 5k/20k |
| **F1.25** | Body de checkin opcional (`data: CheckinRequest | None = None` + defaults) | `app/routers/checkin.py`, `app/services/checkin_service.py` | Contrato (`required: false`) y código alineados |
| **F1.26** | Agregar `/health/db` al openapi.yaml + crear `LICENSE` MIT | `docs/contratos/openapi.yaml`, `LICENSE` | Contrato cubre endpoints reales; template F0-1 completo |

**Nota:** NO tocan dependencias cruzadas (Dev B real, bucket/VM-INGESTA del Lead, contenedor en
`aeropuerto-data-science`, nginx `/api/pasajeros`): esas siguen con mock/contrato y se integran cuando
el otro lado esté listo.

**Nota sobre seed:** `seed_local.py` es **solo para dev/testing local**. El `seeds/` compartido de Dev D (`aeropuerto-data-science/seeds/`, DS-02) genera CSVs para data Science. No reemplaza uno al otro.

### 11-Set · Revisión MS2/MS3 + plan de integración (hoy)

Revisados `ms2-vuelos-api` y `ms3-infraestructura-api` contra el canon `docs/plan/backend.md`.

| Repo | Estado | Gaps |
|---|---|---|
| **MS2** (Dev B) | MS2-01..07 ✓ (`/vuelos/{id}/exists` real + CI GHCR + Swagger `/docs`) | **seed de vuelos** (Hito 1 2–5k → MS2-09 20k con seeds compartidos); MS2-08 tripulación; MS2-10 JVM `t3.small`; MS2-11 pruebas; MS2-12 README/tag |
| **MS3** (Dev C) | Base Express+Mongo + CRUD recursos/incidencias/asignaciones parcial | **MS3-05 NO llama a MS2** (env `MS2_URL=http://localhost:8082` roto: puerto mal y `localhost` desde contenedor); bugs `findByIdAndUpdate(id)` sin body y `error.message` con `error` no definido; MS3-06..10; sin CI GHCR; README vacío |
| **MS1** (yo) | F1 ✓ + evidencias (`smoke_test.txt`, `log_ms1_ms2.txt`, collection Postman) | apuntar `MS2_BASE_URL` a MS2 real; MS1-09 (20k, bloqueado por vuelos de Dev B); informe/E-R; capturas PNG |

**Fase A — MS1→MS2 real (hoy, demo 1 máquina):**
- [ ] Levantar MS2 local (`docker compose up -d --build` en `ms2-vuelos-api`); health
      `GET localhost:8002/api/vuelos/ping`.
- [ ] Confirmar vuelos cargados en MS2 (Dev B); sin datos solo se prueban 422 (`VUELO_NO_EXISTE`) y
      502 (`MS2_NO_DISPONIBLE`) — el happy path espera el seed.
- [ ] MS1 `.env`: `MS2_BASE_URL=http://host.docker.internal:8002` + `extra_hosts` en el
      compose + restart.
- [ ] Probar `POST /tickets` y `POST /equipajes` contra MS2 real; verificar log saliente
      ("Saliente MS1→MS2"); actualizar `log_ms1_ms2.txt` + correr smoke.

**Fase B — Mi cierre F2 (Hito 2):**
- [x] `.github/workflows/build-push-ghcr.yml` (BE-TX-05) **escrito** (12-Set) — se activa al subir repo a GitHub.
- [ ] MS1-09: carga 20k `ticket`/`equipaje` con seeds compartidos (DS-02) + `COUNT(*)`. **Bloqueado por
      vuelos de Dev B.** Script listo: `python -m app.scripts.load_csv`.
- [x] MS1-10: Swagger completo (`docs/contratos/openapi.yaml` con ejemplos/errores 400/404/409/422/502,
      11 paths) + pruebas pytest **32 ✓** (`tests/`).
- [x] MS1-11: README (levantar local / tras corte / vars env / MS2 real / 20k).

**Fase C/D — Avisar a Dev B, Dev C y Lead (no es mi código):**
- Dev B: seed vuelos (Hito 1 → 20k), MS2-08/10/11/12. **Crítico para desbloquear MS1-09 y MS1→MS2 happy path.**
- Dev C: MS3-05 (validar vuelo contra MS2 con `MS2_URL=http://host.docker.internal:8002/api/vuelos`),
  bugs, MS3-06..10, CI GHCR.
- Lead: nginx `/api/pasajeros`→`8001` (BE-TX-06); bucket S3 + VM-INGESTA (DS-04/05) para que corra mi
  `ingesta_ms1.py`; despliegue 2 VM-PROD + ALB + Gateway (BE-INT-01..09).

### F2 — Completar (después de Hito 1, resumen)
- [ ] Carga masiva ≥**20 000** en `ticket` y `equipaje` (una vez) + evidencia `COUNT(*)`.
  *(En la carga se setea `estado_boarding` en `Check-in`/`Embarcado` para Q4 de Athena.)* Script: `python -m app.scripts.load_csv`.
- [x] Swagger completo + ejemplos + pruebas (happy path + validación). — pytest 32 ✓ + openapi con ejemplos.
- [x] README (levantar local / tras corte) — completo. tag `v1.0` + GHCR pendiente de repo en GitHub.
- [ ] Sección del informe + E/R definitivo.
- [ ] Capturas PNG de Swagger/Postman para completar F1.17 (el smoke + logs + collection Postman ya
  existen en `docs/evidencias/backend/`: `smoke_test.txt`, `log_ms1_ms2.txt`, `ms1.postman_collection.json`).

**Resuelto en 10-Set (Fases A/B):** `Dockerfile` prod sin `--reload` (imagen `ms1-pasajeros-api-app`),
`.dockerignore` creado, compose con `command` dev `--reload`, mock MS2 y validación MS1→MS2 probados
(smoke `RESULTADO: OK` sobre `localhost:8001`, log saliente verificado en `docker compose logs`).

**Regla general:** trabajo `contract-first`; si una dependencia (MS2) falta, uso el `openapi.yaml` o
mock y sigo adelante; cada tarea deja evidencia antes de avanzar.
