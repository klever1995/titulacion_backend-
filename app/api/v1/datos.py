# ==============================
# app/api/v1/datos.py
# Consulta de datos crudos y limpios, y valores para los filtros
# ==============================
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import Cuarentena, EncuestaSucia, TicketLimpio, TicketSucio
from app.schemas import ComparacionResponse, TicketLimpioResponse, TicketSucioResponse

router = APIRouter(tags=["Datos"])


@router.get("/sucios", response_model=list[TicketSucioResponse])
def obtener_datos_sucios(limit: int = Query(100, ge=1, le=1000),
                         offset: int = Query(0, ge=0),
                         db: Session = Depends(get_db)):
    """Tickets tal como llegaron (paginados)."""
    return db.query(TicketSucio).offset(offset).limit(limit).all()


@router.get("/limpios", response_model=list[TicketLimpioResponse])
def obtener_datos_limpios(limit: int = Query(100, ge=1, le=1000),
                          offset: int = Query(0, ge=0),
                          db: Session = Depends(get_db)):
    """Tickets después del ETL (paginados)."""
    return db.query(TicketLimpio).offset(offset).limit(limit).all()


@router.get("/filtros")
def obtener_filtros(db: Session = Depends(get_db)):
    """Valores disponibles para los filtros del dashboard."""
    def distintos(columna):
        return sorted(v[0] for v in db.query(columna).distinct() if v[0] is not None)
    return {
        "categorias": distintos(TicketLimpio.categoria),
        "canales": distintos(TicketLimpio.canal),
        "agentes": distintos(TicketLimpio.agente),
        "segmentos": distintos(TicketLimpio.segmento),
        "estados": distintos(TicketLimpio.estado),
    }


@router.get("/comparar/{id_ticket}", response_model=ComparacionResponse)
def comparar_ticket(id_ticket: str, db: Session = Depends(get_db)):
    """Un mismo ticket antes y después del ETL, con sus incidencias."""
    id_ticket = id_ticket.strip().upper()
    sucios = db.query(TicketSucio).filter(TicketSucio.id_ticket == id_ticket).all()
    limpio = db.query(TicketLimpio).filter(TicketLimpio.id_ticket == id_ticket).first()
    if not sucios and not limpio:
        raise HTTPException(status_code=404, detail=f"No existe el ticket {id_ticket}")
    encuestas_sucias = (db.query(EncuestaSucia)
                        .filter(func.upper(func.trim(EncuestaSucia.id_ticket)) == id_ticket)
                        .all())
    # Incidencias de cualquier fuente (tickets y encuestas guardan el id_ticket como id_registro)
    incidencias = (db.query(Cuarentena)
                   .filter(Cuarentena.id_registro == id_ticket)
                   .order_by(Cuarentena.id)
                   .all())
    return {"sucios": sucios, "encuestas_sucias": encuestas_sucias,
            "limpio": limpio, "incidencias": incidencias}