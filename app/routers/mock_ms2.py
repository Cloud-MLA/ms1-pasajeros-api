import random

from fastapi import APIRouter, HTTPException

from app.schemas.enums import EstadoVuelo

router = APIRouter(prefix="/ms2", tags=["MS2 Mock"])

# Fallback de dev bajo el contrato real de MS2: permite apuntar
# MS2_BASE_URL al propio MS1 (http://app:8001) cuando MS2 no está.
mock_vuelos_router = APIRouter(prefix="/api/vuelos", tags=["MS2 Mock"])

_ESTADO_VUEO_VALUES = [e.value for e in EstadoVuelo]


def _mock_vuelo_exists(id_vuelo: int):
    if id_vuelo < 1 or id_vuelo > 25000:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NO_ENCONTRADO", "message": f"Vuelo {id_vuelo} no encontrado"}
        })
    rng = random.Random(id_vuelo)
    estado = rng.choice(_ESTADO_VUEO_VALUES)
    return {"exists": True, "id_vuelo": id_vuelo, "estado": estado}


@router.get("/vuelos/{id_vuelo}/exists")
def mock_vuelo_exists(id_vuelo: int):
    return _mock_vuelo_exists(id_vuelo)


@mock_vuelos_router.get("/{id_vuelo}/exists")
def mock_vuelo_exists_api(id_vuelo: int):
    return _mock_vuelo_exists(id_vuelo)