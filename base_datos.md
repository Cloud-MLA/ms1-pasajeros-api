# Base de Datos — MS1 (Pasajeros / Tickets)

Modelo de datos de **`pasajeros_db`** (MySQL 8) para el microservicio **MS1 Pasajeros / Tickets**.
Fuente: `docs/fuentes/modelo-datos-aeropuerto-jorge-chavez.pdf` (proyecto Base de Datos I) y la
transformación de `docs/requerimientos.md` §2–§3.

---

## 1. Modelo Entidad-Relación (notación de Peter Chen)

Entidades (rectángulos): `PERSONA`, `CATEGORIA_MIGRATORIA`, `PASAJERO`, `TICKET`, `CHECKIN`,
`EQUIPAJE`.

Relaciones (rombos ♢): la cardinalidad se marca en **cada extremo** de la línea que une el rombo con
la entidad (`1`, `N` o `M`).

### 1.1 Relaciones internas de MS1

| Rombo (relación) | Entidad A | Card. A | Card. B | Entidad B | Participación |
|---|---|---|---|---|---|
| ♢ **ES_1_1** | PERSONA | 1 | 1 | PASAJERO | Pasajero **total** · Persona parcial (IsA parcial y disjunta) |
| ♢ **PERTENECE** | CATEGORIA_MIGRATORIA | 1 | N | PASAJERO | Pasajero **total** (todo pasajero tiene categoría) |
| ♢ **EMITE** | PASAJERO | 1 | N | TICKET | Ticket **total** (todo ticket tiene pasajero) |
| ♢ **REALIZA** | TICKET | 1 | 1 | CHECKIN | Checkin **total** · Ticket parcial (0..1 checkin) |
| ♢ **REGISTRA** | PASAJERO | 1 | N | EQUIPAJE | Equipaje **total** (todo equipaje tiene dueño) |

Lectura de cada cardinalidad:

- **PERSONA —1:1— PASAJERO**: una `persona` puede ser **una** `pasajero`; un `pasajero` es **una**
  única `persona` (comparten `id_persona` como PK/FK).
- **CATEGORIA_MIGRATORIA —1:N— PASAJERO**: una `categoria_migratoria` agrupa **N** `pasajero`; cada
  `pasajero` pertenece a **1** sola categoría.
- **PASAJERO —1:N— TICKET**: un `pasajero` emite **N** `ticket`; cada `ticket` pertenece a **1**
  único `pasajero`.
- **TICKET —1:1— CHECKIN**: un `ticket` tiene **a lo sumo 1** `checkin`; cada `checkin` corresponde a
  **exactamente 1** `ticket` (`id_ticket` compartido como PK/FK, entidad débil).
- **PASAJERO —1:N— EQUIPAJE**: un `pasajero` registra **N** `equipaje`; cada `equipaje` pertenece a
  **1** único `pasajero`.

### 1.2 Referencias suaves a MS2 (no se dibujan como FK en el E/R)

Solo referencia lógica (REST), **sin rombo físico** en el E/R de MS1:

| Referencia | Entidad de MS1 | Card. A | Card. B | Entidad externa | Validación |
|---|---|---|---|---|---|
| VUELA_EN (soft) | TICKET | N | 1 | VUELO (MS2) | REST `GET /vuelos/{id}/exists` al crear ticket |
| VUELA_EN (soft) | EQUIPAJE | N | 1 | VUELO (MS2) | REST contra `VUELO` de MS2 |

### 1.3 Resumen

- **Sin relaciones N:M** (muchos a muchos) en MS1.
- Relaciones: **2 de 1:1** (ES_1_1, REALIZA) y **3 de 1:N** (PERTENECE, EMITE, REGISTRA).
- Participación **total** (doble línea en Chen) en el lado donde el atributo es `NOT NULL`: pasajero,
  ticket, checkin, equipaje.

---

## 2. Modelo Relacional

6 tablas. Notación: subrayado = PK; `FK` = clave foránea física; columna = atributo exacto del modelo
fuente. `ESTADO_BOARDING` y `TIPO_DOCUMENTO` se implementan como `ENUM` de MySQL con los valores de
`docs/contratos/enums.md`.

### `PERSONA`
| Columna | Tipo | PK | FK | Restricciones |
|---|---|---|---|---|
| `id_persona` | INT AUTO_INCREMENT | PK | — | identidad |
| `nombre` | VARCHAR(50) | — | — | NOT NULL |
| `apellido` | VARCHAR(50) | — | — | NOT NULL |
| `fecha_nacimiento` | DATE | — | — | NOT NULL |

### `CATEGORIA_MIGRATORIA`
| Columna | Tipo | PK | FK | Restricciones |
|---|---|---|---|---|
| `id` | INT AUTO_INCREMENT | PK | — | identidad |
| `nombre` | ENUM(`Nacional`,`Internacional`,`Transito`) | — | — | NOT NULL |
| `tarifa` | DECIMAL(10,2) | — | — | NOT NULL · CHECK(`tarifa >= 0`) |

### `PASAJERO`
| Columna | Tipo | PK | FK | Restricciones |
|---|---|---|---|---|
| `id_persona` | INT | PK | FK → `PERSONA.id_persona` | ON DELETE CASCADE · ON UPDATE CASCADE |
| `tipo_documento` | ENUM(`DNI`,`Pasaporte`,`Carnet de Extranjeria`) | — | — | NOT NULL · parte de UNIQUE |
| `numero_documento` | VARCHAR(15) | — | — | NOT NULL · parte de UNIQUE |
| `id_categoria` | INT | — | FK → `CATEGORIA_MIGRATORIA.id` | NOT NULL · ON DELETE RESTRICT |

**UNIQUE(`tipo_documento`, `numero_documento`)**

### `TICKET`
| Columna | Tipo | PK | FK | Restricciones |
|---|---|---|---|---|
| `id_ticket` | BIGINT AUTO_INCREMENT | PK | — | identidad · rango 1 – 60 000 |
| `precio` | NUMERIC(10,2) | — | — | NOT NULL |
| `fecha_emision` | DATE | — | — | NOT NULL |
| `estado_boarding` | ENUM(`Emitido`,`Check-in`,`Embarcado`,`No-show`,`Cancelado`) | — | — | NOT NULL · DEFAULT `Emitido` |
| `id_vuelo` | BIGINT | — | **soft → MS2** | NOT NULL · sin FK física · validado por REST |
| `id_persona` | INT | — | FK → `PERSONA.id_persona` | NOT NULL |

### `CHECKIN`
| Columna | Tipo | PK | FK | Restricciones |
|---|---|---|---|---|
| `id_ticket` | BIGINT | PK | FK → `TICKET.id_ticket` | ON DELETE CASCADE · ON UPDATE CASCADE |
| `fecha_hora` | TIMESTAMP | — | — | NOT NULL · DEFAULT NOW() |
| `counter` | VARCHAR(10) | — | — | — |
| `con_equipaje` | BOOLEAN | — | — | NOT NULL · DEFAULT FALSE |

Entidad **débil** respecto de `TICKET` (1:1).

### `EQUIPAJE`
| Columna | Tipo | PK | FK | Restricciones |
|---|---|---|---|---|
| `id` | VARCHAR(20) | PK | — | Tag ID (BHS) |
| `peso` | NUMERIC(6,2) | — | — | NOT NULL · CHECK(`peso > 0`) |
| `id_persona` | INT | — | FK → `PERSONA.id_persona` | NOT NULL · ON DELETE RESTRICT |
| `id_vuelo` | BIGINT | — | **soft → MS2** | NOT NULL · sin FK física · validado por REST |

---

## 3. Transformación conceptual → relacional (resumen)

- **ES_1_1** (PERSONA–PASAJERO) → `PASAJERO.id_persona` es PK **y** FK a `PERSONA` (tabla por subclase).
- **PERTENECE 1:N** → `PASAJERO.id_categoria` (FK a `CATEGORIA_MIGRATORIA.id`).
- **EMITE 1:N** → `TICKET.id_persona` (FK a `PERSONA.id_persona`).
- **REALIZA 1:1** → `CHECKIN.id_ticket` es PK **y** FK a `TICKET.id_ticket`, con `ON DELETE CASCADE`.
- **REGISTRA 1:N** → `EQUIPAJE.id_persona` (FK a `PERSONA.id_persona`).
- **VUELA_EN (soft)** → `TICKET.id_vuelo` y `EQUIPAJE.id_vuelo` **no** son FK; se validan por REST contra MS2.