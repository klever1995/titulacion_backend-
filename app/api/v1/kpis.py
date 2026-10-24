from datetime import date
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import TicketLimpio
from app.schemas import KPIsResponse
from app.services.kpi_service import (
    AGRUPABLES,
    COLUMNAS,
    calcular_kpis,
    filtrar,
    kpis_por_grupo,
)
from app.services.ml_service import analizar_factores_incumplimiento

router = APIRouter(tags=["KPIs y análisis"])


def _tickets(db: Session, categoria, canal, agente, segmento, desde, hasta) -> pd.DataFrame:
    """Carga los tickets limpios desde la base y aplica los filtros recibidos."""
    filas = db.query(*[getattr(TicketLimpio, c) for c in COLUMNAS]).all()
    df = pd.DataFrame(filas, columns=COLUMNAS)
    if not df.empty:
        df["fecha_apertura"] = pd.to_datetime(df["fecha_apertura"])
    return filtrar(df, categoria, canal, agente, segmento, desde, hasta) if not df.empty else df


@router.get("/kpis", response_model=KPIsResponse)
def obtener_kpis(
    categoria: Optional[str] = None,
    canal: Optional[str] = None,
    agente: Optional[str] = None,
    segmento: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """KPIs globales o filtrados por categoría, canal, agente, segmento y período."""
    df = _tickets(db, categoria, canal, agente, segmento, desde, hasta)
    return calcular_kpis(df if not df.empty else pd.DataFrame(columns=COLUMNAS))


@router.get("/kpis/desglose")
def obtener_desglose(
    por: str = Query("canal"),
    categoria: Optional[str] = None,
    canal: Optional[str] = None,
    agente: Optional[str] = None,
    segmento: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """KPIs separados por canal, categoría, agente, segmento, estado o mes/año."""
    opciones_validas = AGRUPABLES + ["mes", "anio"]
    if por not in opciones_validas:
        raise HTTPException(
            status_code=400, detail=f"'por' debe ser uno de {opciones_validas}"
        )

    df = _tickets(db, categoria, canal, agente, segmento, desde, hasta)
    if df.empty:
        return []

    if por == "mes":
        df["mes"] = df["fecha_apertura"].dt.strftime("%Y-%m")
        return kpis_por_grupo(df, "mes")
    if por == "anio":
        df["anio"] = df["fecha_apertura"].dt.year
        return kpis_por_grupo(df, "anio")

    return kpis_por_grupo(df, por)


@router.get("/analisis-factores")
def obtener_analisis_factores(db: Session = Depends(get_db)):
    """Ejecuta el modelo de regresión logística sobre los tickets limpios."""
    resultado = analizar_factores_incumplimiento(db)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado