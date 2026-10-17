# ==============================
# app/services/etl_service.py
# Lógica de negocio para el proceso ETL
# ==============================
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models import TicketLimpio, TicketSucio

def procesar_y_guardar(crm_path: str, tickets_path: str, encuestas_path: str, db: Session):
    # 1. Leer archivos
    df_crm = pd.read_csv(crm_path)
    df_tickets = pd.read_csv(tickets_path)
    df_encuestas = pd.read_csv(encuestas_path)

    # --- GUARDAR EL "ANTES" EN LA BD (Tabla Sucios) ---
    db.query(TicketSucio).delete() # Limpiar tabla antes de insertar
    for _, row in df_tickets.head(100).iterrows(): # Guardamos 100 para el dashboard
        sucio = TicketSucio(
            id_ticket=str(row['id_ticket']),
            id_cliente=str(row['id_cliente']) if pd.notna(row['id_cliente']) else None,
            fecha_apertura=str(row['fecha_apertura']) if pd.notna(row['fecha_apertura']) else None,
            fecha_cierre=str(row['fecha_cierre']) if pd.notna(row['fecha_cierre']) else None,
            categoria=str(row['categoria']),
            canal=str(row['canal']),
            estado=str(row['estado']),
            agente=str(row['agente']),
            reabierto=int(row['reabierto']),
            sla_objetivo_horas=float(row['sla_objetivo_horas'])
        )
        db.add(sucio)
    db.commit()

    # --- INICIA EL ETL (LIMPIEZA) ---
    df_crm['id_cliente'] = df_crm['id_cliente'].str.strip().str.upper()
    
    df_tickets['id_cliente'] = df_tickets['id_cliente'].astype(str).str.replace('-', '').str.strip().str.upper()
    df_tickets['id_cliente'] = df_tickets['id_cliente'].replace(['NONE', 'NAN'], np.nan)
    df_tickets['fecha_apertura'] = pd.to_datetime(df_tickets['fecha_apertura'], dayfirst=True, errors='coerce')
    df_tickets['fecha_cierre'] = pd.to_datetime(df_tickets['fecha_cierre'], dayfirst=True, errors='coerce')
    df_tickets['categoria'] = df_tickets['categoria'].str.strip().str.title()
    
    df_encuestas['id_cliente'] = df_encuestas['id_cliente'].str.strip().str.upper()

    # Unión (Merge)
    df_final = pd.merge(df_tickets, df_crm, on='id_cliente', how='left')
    df_final = pd.merge(df_final, df_encuestas, on='id_cliente', how='left')

    # Cálculos
    df_final['tiempo_resolucion_horas'] = (df_final['fecha_cierre'] - df_final['fecha_apertura']).dt.total_seconds() / 3600
    df_final['tiempo_resolucion_horas'] = df_final['tiempo_resolucion_horas'].fillna(0)

    # --- GUARDAR EL "DESPUÉS" EN LA BD (Tabla Limpios) ---
    db.query(TicketLimpio).delete()
    for _, row in df_final.iterrows():
        nuevo_ticket = TicketLimpio(
            id_ticket=str(row['id_ticket']),
            id_cliente=str(row['id_cliente']) if pd.notna(row['id_cliente']) else None,
            fecha_apertura=str(row['fecha_apertura']),
            fecha_cierre=str(row['fecha_cierre']) if pd.notna(row['fecha_cierre']) else None,
            categoria=str(row['categoria']),
            canal=str(row['canal']),
            estado=str(row['estado']),
            agente=str(row['agente']),
            reabierto=int(row['reabierto']),
            sla_objetivo_horas=float(row['sla_objetivo_horas']),
            segmento=str(row['segmento']) if pd.notna(row['segmento']) else None,
            satisfaccion=float(row['satisfaccion']) if pd.notna(row['satisfaccion']) else None,
            tiempo_resolucion_horas=float(row['tiempo_resolucion_horas'])
        )
        db.add(nuevo_ticket)
    
    db.commit()
    return len(df_final)