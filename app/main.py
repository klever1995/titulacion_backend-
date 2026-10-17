# ==============================
# app/main.py
# Punto de entrada de la API
# ==============================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Importamos el archivo endpoints.py directamente
from app.api.v1 import endpoints 

from app.db.base import Base, engine
# Importar los modelos para que SQLAlchemy los detecte
from app.models import TicketSucio, TicketLimpio

# 2. Creamos las tablas en la base de datos automáticamente
Base.metadata.create_all(bind=engine)

# 3. Inicializamos FastAPI
app = FastAPI(title="API - Proyecto BI Complexivo")

# 4. Configurar CORS para que React pueda hacer peticiones
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Incluimos las rutas de endpoints.py
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Backend del Proyecto BI funcionando correctamente"}