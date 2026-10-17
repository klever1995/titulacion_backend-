# ==============================
# app/api/v1/endpoints.py
# Endpoints para el ETL y consulta de datos
# ==============================
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models import TicketLimpio, TicketSucio
from app.schemas import TicketLimpioResponse, TicketSucioResponse, KPIsResponse
from app.services.etl_service import procesar_y_guardar
import shutil
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["tickets"]) # Sin prefijo

# ==============================
# 1. Subir archivos y ejecutar ETL
# ==============================
@router.post("/upload-etl", status_code=status.HTTP_201_CREATED)
async def ejecutar_etl(
    crm: UploadFile = File(...), 
    tickets: UploadFile = File(...), 
    encuestas: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    os.makedirs("data", exist_ok=True)
    crm_path, ticks_path, enc_path = "data/crm.csv", "data/tickets.csv", "data/encuestas.csv"
    
    with open(crm_path, "wb") as buffer: shutil.copyfileobj(crm.file, buffer)
    with open(ticks_path, "wb") as buffer: shutil.copyfileobj(tickets.file, buffer)
    with open(enc_path, "wb") as buffer: shutil.copyfileobj(encuestas.file, buffer)

    try:
        total = procesar_y_guardar(crm_path, ticks_path, enc_path, db)
        logger.info(f"ETL ejecutado exitosamente. {total} tickets procesados.")
        return {"message": f"ETL ejecutado. {total} tickets guardados en la BD."}
    except Exception as e:
        logger.error(f"Error en ETL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# 2. Obtener los datos del "Antes"
# ==============================
@router.get("/sucios", response_model=list[TicketSucioResponse])
async def obtener_datos_sucios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Devuelve los tickets originales sin procesar (El 'Antes')"""
    return db.query(TicketSucio).offset(skip).limit(limit).all()

# ==============================
# 3. Obtener los datos del "Después"
# ==============================
@router.get("/limpios", response_model=list[TicketLimpioResponse])
async def obtener_datos_limpios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Devuelve los tickets procesados y limpios (El 'Después')"""
    return db.query(TicketLimpio).offset(skip).limit(limit).all()

# ==============================
# 4. Obtener los KPIs calculados en tiempo real
# ==============================
@router.get("/kpis", response_model=KPIsResponse)
async def obtener_kpis(db: Session = Depends(get_db)):
    tickets = db.query(TicketLimpio).all()
    if not tickets:
        return KPIsResponse(total_tickets=0, tiempo_promedio=0, satisfaccion_promedio=0, reincidencia=0)

    total = len(tickets)
    tiempo_prom = sum([t.tiempo_resolucion_horas for t in tickets]) / total
    satisfacciones = [t.satisfaccion for t in tickets if t.satisfaccion is not None]
    satis_prom = sum(satisfacciones) / len(satisfacciones) if satisfacciones else 0
    reincidencia = (sum([t.reabierto for t in tickets]) / total) * 100

    return KPIsResponse(
        total_tickets=total,
        tiempo_promedio=round(tiempo_prom, 2),
        satisfaccion_promedio=round(satis_prom, 2),
        reincidencia=round(reincidencia, 2)
    )