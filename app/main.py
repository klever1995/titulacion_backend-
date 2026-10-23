# ==============================
# app/main.py
# Punto de entrada de la API
# ==============================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import endpoints
from app.db.base import Base, engine
# Importar todos los modelos para que SQLAlchemy cree sus tablas
from app.models import (  # noqa: F401
    Cuarentena, CrmSucio, EncuestaSucia, ReporteCalidad, TicketLimpio, TicketSucio,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API - Proyecto BI Complexivo")

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
    return {"message": "Backend del Proyecto BI funcionando correctamente"}