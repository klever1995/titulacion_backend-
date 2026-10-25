import logging
import os
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import Cuarentena, TicketLimpio, TicketSucio
from app.services.etl_service import procesar_y_guardar

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/etl", tags=["ETL"])

# Rutas de los CSV crudos dentro del contenedor
DIR_RAW = "data/raw"
RUTA_CRM = f"{DIR_RAW}/crm_sucio.csv"
RUTA_TICKETS = f"{DIR_RAW}/tickets_sucio.csv"
RUTA_ENCUESTAS = f"{DIR_RAW}/encuestas_sucio.csv"

# NUEVO: Diccionario en memoria para guardar el resumen de encuestas
# (Se borra al reiniciar el servidor, pero se mantiene mientras esté encendido)
RESUMEN_ENCUESTAS_MEMORIA = {}


def _correr(db: Session):
    """Ejecuta el ETL sobre los CSV de data/raw y maneja errores de base."""
    global RESUMEN_ENCUESTAS_MEMORIA  # NUEVO: Para poder modificar la variable global
    
    try:
        resultado = procesar_y_guardar(RUTA_CRM, RUTA_TICKETS, RUTA_ENCUESTAS, db)
        
        # NUEVO: Guardamos el resumen de encuestas en la memoria
        if "emparejamiento_encuestas" in resultado:
            RESUMEN_ENCUESTAS_MEMORIA = resultado["emparejamiento_encuestas"]
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error en ETL: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el ETL: {e}")
    logger.info(f"ETL ejecutado. {resultado['total_tickets']} tickets procesados.")
    return resultado


@router.post("/ejecutar", status_code=status.HTTP_201_CREATED)
def ejecutar_con_archivos_locales(db: Session = Depends(get_db)):
    """Ejecuta el ETL con los CSV que ya están en data/raw (no sube nada)."""
    for ruta in (RUTA_CRM, RUTA_TICKETS, RUTA_ENCUESTAS):
        if not os.path.exists(ruta):
            raise HTTPException(status_code=404, detail=f"No se encontró {ruta}")
    return _correr(db)


@router.post("/subir", status_code=status.HTTP_201_CREATED)
def subir_archivos(
    crm: UploadFile = File(...),
    tickets: UploadFile = File(...),
    encuestas: UploadFile = File(...),
    ejecutar: bool = False,
    db: Session = Depends(get_db),
):
    """Guarda los 3 CSV en data/raw. Con ?ejecutar=true también corre el ETL."""
    os.makedirs(DIR_RAW, exist_ok=True)
    for archivo, ruta in [
        (crm, RUTA_CRM),
        (tickets, RUTA_TICKETS),
        (encuestas, RUTA_ENCUESTAS),
    ]:
        with open(ruta, "wb") as destino:
            shutil.copyfileobj(archivo.file, destino)
    if ejecutar:
        return _correr(db)
    return {
        "mensaje": "Archivos guardados en data/raw. Revisa el perfilado y luego ejecuta el ETL."
    }


@router.get("/resumen")
def resumen_etl(db: Session = Depends(get_db)):
    """Estado del último ETL, leído de la base de datos y de la memoria."""
    global RESUMEN_ENCUESTAS_MEMORIA  # NUEVO: Para poder leer la variable global
    
    limpios = db.query(func.count(TicketLimpio.id)).scalar() or 0
    crudos = db.query(func.count(TicketSucio.id)).scalar() or 0
    match = {
        (m or "sin_dato"): n
        for m, n in db.query(TicketLimpio.metodo_match, func.count())
        .group_by(TicketLimpio.metodo_match)
        .all()
    }
    cuarentena = [
        {"fuente": f, "motivo": m, "cantidad": n}
        for f, m, n in db.query(Cuarentena.fuente, Cuarentena.motivo, func.count())
        .group_by(Cuarentena.fuente, Cuarentena.motivo)
        .order_by(func.count().desc())
        .all()
    ]
    
    return {
        "etl_ejecutado": limpios > 0,
        "tickets_crudos": crudos,
        "tickets_limpios": limpios,
        "emparejamiento_clientes": match,
        "emparejamiento_encuestas": RESUMEN_ENCUESTAS_MEMORIA, 
        "cuarentena": cuarentena,
        "total_cuarentena": sum(c["cantidad"] for c in cuarentena),
    }