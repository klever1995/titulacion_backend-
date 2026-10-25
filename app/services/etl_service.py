import pandas as pd
from sqlalchemy.orm import Session

from app.models import (
    Cuarentena,
    CrmSucio,
    EncuestaSucia,
    ReporteCalidad,
    TicketLimpio,
    TicketSucio,
)
from app.services.limpieza_service import ejecutar_etl
from app.services.quality_service import evaluar_calidad, resumir

# Columnas que se copian del DataFrame limpio a la tabla tickets_limpios
COLUMNAS_LIMPIO = [
    "id_ticket", "id_cliente", "metodo_match", "fecha_apertura", "fecha_cierre",
    "categoria", "canal", "estado", "agente", "reabierto", "sla_objetivo_horas",
    "segmento", "satisfaccion", "tiempo_resolucion_horas", "incumple_sla",
]

def _registros(df: pd.DataFrame, columnas: list) -> list:
    """DataFrame a lista de dicts, con los vacíos convertidos a None."""
    d = df[columnas].astype(object)
    d = d.where(d.notna(), None)
    return d.to_dict("records")

def procesar_y_guardar(crm_path: str, tickets_path: str, encuestas_path: str, db: Session):
    """Ejecuta el ETL completo: guarda el antes, limpia, mide calidad y guarda el después."""
    # Lectura cruda como texto para no perder los defectos originales
    crm_raw = pd.read_csv(crm_path, dtype=str)
    tickets_raw = pd.read_csv(tickets_path, dtype=str)
    encuestas_raw = pd.read_csv(encuestas_path, dtype=str)

    # Calidad antes del ETL
    ids_crm_crudo = set(crm_raw["id_cliente"].dropna().astype(str))
    filas_antes = evaluar_calidad(crm_raw, tickets_raw, encuestas_raw, ids_crm_crudo, "antes")

    # Persistencia de los datos crudos como evidencia
    for modelo in (TicketSucio, CrmSucio, EncuestaSucia):
        db.query(modelo).delete()
    db.bulk_insert_mappings(TicketSucio, _registros(tickets_raw, list(tickets_raw.columns)))
    db.bulk_insert_mappings(CrmSucio, _registros(crm_raw, list(crm_raw.columns)))
    db.bulk_insert_mappings(EncuestaSucia, _registros(encuestas_raw, list(encuestas_raw.columns)))
    db.commit()

    # Limpieza, emparejamiento y métricas
    crm, tickets, encuestas, cuarentena, resumen_match, resumen_match_encuestas = ejecutar_etl(
        crm_raw, tickets_raw, encuestas_raw
    )

    # Calidad después del ETL con las mismas reglas
    filas_despues = evaluar_calidad(crm, tickets, encuestas, set(crm["id_cliente"]), "despues")

    # Persistencia de resultados limpios y reportes
    for modelo in (TicketLimpio, Cuarentena, ReporteCalidad):
        db.query(modelo).delete()
    db.bulk_insert_mappings(TicketLimpio, _registros(tickets, COLUMNAS_LIMPIO))
    db.bulk_insert_mappings(Cuarentena, cuarentena)
    db.bulk_insert_mappings(ReporteCalidad, filas_antes + filas_despues)
    db.commit()

    return {
        "total_tickets": len(tickets),
        "calidad_antes": resumir(filas_antes),
        "calidad_despues": resumir(filas_despues),
        "registros_en_cuarentena": len(cuarentena),
        "emparejamiento_clientes": resumen_match,
        "emparejamiento_encuestas": resumen_match_encuestas, 
    }