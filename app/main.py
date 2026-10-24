from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import endpoints
from app.db.base import Base, engine

# Importar los modelos registra sus tablas en Base antes del create_all
from app.models import (  # noqa: F401
    Cuarentena,
    CrmSucio,
    EncuestaSucia,
    ReporteCalidad,
    TicketLimpio,
    TicketSucio,
)

# Crea las tablas al arrancar (si ya existen, no hace nada)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API - Proyecto BI Complexivo")

# CORS abierto para permitir las peticiones del frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")


@app.get("/")
def root():
    """Comprobación rápida de que la API está en pie."""
    return {"message": "Backend del Proyecto BI funcionando correctamente"}