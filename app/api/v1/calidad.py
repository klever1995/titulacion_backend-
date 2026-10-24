import os
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.etl import RUTA_CRM, RUTA_ENCUESTAS, RUTA_TICKETS
from app.db.base import get_db
from app.models import Cuarentena, ReporteCalidad
from app.schemas import CalidadDatosResponse, CuarentenaResponse, ReglaCalidadResponse
from app.services.profiling_service import perfilar_fuentes
from app.services.quality_service import resumir

router = APIRouter(tags=["Calidad de datos"])


@router.get("/perfilado")
def obtener_perfilado():
    """Describe los problemas de los datos crudos (antes de limpiar)."""
    for ruta in (RUTA_CRM, RUTA_TICKETS, RUTA_ENCUESTAS):
        if not os.path.exists(ruta):
            raise HTTPException(status_code=404, detail=f"No se encontró {ruta}")
    return perfilar_fuentes(
        pd.read_csv(RUTA_CRM, dtype=str),
        pd.read_csv(RUTA_TICKETS, dtype=str),
        pd.read_csv(RUTA_ENCUESTAS, dtype=str),
    )


@router.get("/calidad", response_model=CalidadDatosResponse)
def obtener_calidad(db: Session = Depends(get_db)):
    """Puntaje por dimensión antes y después del ETL (se lee de la base, no de memoria)."""
    filas = db.query(ReporteCalidad).all()
    if not filas:
        raise HTTPException(status_code=404, detail="Aún no se ha ejecutado ningún ETL.")
    por_etapa = {}
    for etapa in ("antes", "despues"):
        por_etapa[etapa] = resumir(
            [{"dimension": f.dimension, "puntaje": f.puntaje} for f in filas if f.etapa == etapa]
        )
    a, d = por_etapa["antes"], por_etapa["despues"]
    return CalidadDatosResponse(
        completitud_antes=a["completitud"],
        unicidad_antes=a["unicidad"],
        consistencia_antes=a["consistencia"],
        validez_antes=a["validez"],
        puntaje_total_antes=a["total"],
        completitud_despues=d["completitud"],
        unicidad_despues=d["unicidad"],
        consistencia_despues=d["consistencia"],
        validez_despues=d["validez"],
        puntaje_total_despues=d["total"],
    )


@router.get("/calidad/reglas", response_model=list[ReglaCalidadResponse])
def obtener_reglas(
    etapa: Optional[str] = Query(None, pattern="^(antes|despues)$"),
    fuente: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Detalle de cada regla de calidad, con filtros opcionales."""
    consulta = db.query(ReporteCalidad)
    if etapa:
        consulta = consulta.filter(ReporteCalidad.etapa == etapa)
    if fuente:
        consulta = consulta.filter(ReporteCalidad.fuente == fuente)
    return consulta.order_by(ReporteCalidad.fuente, ReporteCalidad.dimension).all()


@router.get("/cuarentena", response_model=list[CuarentenaResponse])
def obtener_cuarentena(
    fuente: Optional[str] = None,
    motivo: Optional[str] = None,
    id_registro: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Registros que no se pudieron corregir o emparejar con seguridad."""
    consulta = db.query(Cuarentena)
    if fuente:
        consulta = consulta.filter(Cuarentena.fuente == fuente)
    if motivo:
        consulta = consulta.filter(Cuarentena.motivo == motivo)
    if id_registro:
        consulta = consulta.filter(Cuarentena.id_registro == id_registro.strip().upper())
    return consulta.order_by(Cuarentena.id).offset(offset).limit(limit).all()