# ==============================
# app/api/v1/endpoints.py
# Reúne todos los routers de la versión 1 de la API
# ==============================
from fastapi import APIRouter
 
from app.api.v1 import calidad, datos, etl, kpis
 
router = APIRouter()
router.include_router(etl.router)
router.include_router(calidad.router)
router.include_router(datos.router)
router.include_router(kpis.router)
 