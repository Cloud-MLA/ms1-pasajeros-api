import logging

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.categorias import router as categorias_router
from app.routers.pasajeros import router as pasajeros_router
from app.routers.mock_ms2 import router as mock_ms2_router, mock_vuelos_router
from app.routers.tickets import router as tickets_router
from app.routers.checkin import router as checkin_router
from app.routers.equipajes import router as equipajes_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title="MS1 - Pasajeros / Tickets API")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": str(exc.status_code), "message": str(exc.detail)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " → ".join(str(x) for x in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg', '')}")
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDACION", "message": "; ".join(errors)}},
    )


app.include_router(categorias_router)
app.include_router(pasajeros_router)
app.include_router(mock_ms2_router)
app.include_router(mock_vuelos_router)
app.include_router(tickets_router)
app.include_router(checkin_router)
app.include_router(equipajes_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ms1-pasajeros"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
