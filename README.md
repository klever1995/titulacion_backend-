Plataforma Analítica para Calidad del Servicio y Satisfacción

Descripción del Proyecto

Esta plataforma es una solución de Inteligencia de Negocios (BI) diseñada para integrar, limpiar y analizar datos de tres fuentes independientes de una empresa de servicios: un CRM (clientes), una Mesa de Ayuda (tickets) y un sistema de Encuestas (satisfacción).

El objetivo principal es resolver el problema de la mala calidad de los datos y la falta de integración entre sistemas. El sistema aplica un proceso ETL (Extract, Transform, Load) para estandarizar los datos, resolver duplicados, emparejar clientes y calcular métricas clave (KPIs) y modelos predictivos (Machine Learning) que permiten a la gerencia tomar decisiones basadas en evidencia.

Arquitectura y Tecnologías

El proyecto está dividido en dos repositorios principales:

Backend: API REST construida con FastAPI (Python) y base de datos PostgreSQL (con SQLAlchemy).

Frontend: Interfaz de usuario interactiva construida con React y Vite, usando Recharts para las visualizaciones.

Tecnologías clave:

Python 3.11

Pandas y Numpy (Procesamiento y limpieza de datos)

Scikit-Learn (Modelo de Regresión Logística para el análisis de factores)

Docker y Docker Compose (Contenerización y despliegue)

PostgreSQL 15 (Base de datos relacional)

React + Vite (Frontend)

Recharts (Gráficos interactivos)

Requisitos Previos

Para levantar este proyecto localmente necesitas:

Tener instalado Docker y Docker Compose.

Tener instalado Git.

Tener instalado Node.js (para el frontend).

Instalación y Ejecución (Local)

Backend

Clona este repositorio:

git clone https://github.com/klever1995/titulacion_backend-.git
cd titulacion_backend-


Ejecuta Docker Compose para levantar la API y la base de datos:

docker compose up -d --build


La API estará disponible en http://localhost:8010 y la documentación Swagger en http://localhost:8010/docs.

Frontend

Clona el repositorio del frontend:

git clone https://github.com/klever1995/titulacion_frontend.git
cd titulacion_frontend


Instala las dependencias:

npm install


Ejecuta el servidor de desarrollo:

npm run dev


Abre el navegador en http://localhost:5173 (o el puerto que indique Vite).

Flujo del Proceso ETL

El sistema ejecuta el siguiente flujo a través de la interfaz:

Carga: Sube los 3 archivos CSV (crudos) o usa los datos de ejemplo precargados en data/raw.

Perfilado: Análisis de la calidad de los datos crudos (nulos, duplicados, formatos).

Limpieza (ETL):

Estandarización de fechas y catálogos.

Resolución de duplicados.

Emparejamiento de clientes en 3 niveles (Exacto, Normalizado, Difuso).

Cálculo de tiempos de resolución e incumplimiento de SLA.

Resultados: Visualización de los tickets limpios, incidencias en cuarentena y reporte de calidad antes/después.

KPIs: Dashboard interactivo con los indicadores clave.

Machine Learning: Regresión logística para identificar factores de riesgo en el incumplimiento del SLA.

Estructura del Backend

app/api/v1/: Endpoints de la API (calidad, datos, etl, kpis).

app/models/: Modelos de SQLAlchemy (tablas de la base de datos).

app/schemas/: Esquemas de Pydantic (validación de datos).

app/services/: Lógica de negocio (limpieza, emparejamiento, calidad, KPIs, ML).

data/raw/: Archivos CSV crudos para el ETL.

Endpoints Principales

POST /api/v1/etl/subir: Sube los archivos CSV.

POST /api/v1/etl/ejecutar: Ejecuta el ETL.

GET /api/v1/etl/resumen: Resumen del último ETL ejecutado.

GET /api/v1/perfilado: Diagnóstico de datos crudos.

GET /api/v1/calidad: Puntajes de calidad antes y después.

GET /api/v1/cuarentena: Registros que no se pudieron corregir.

GET /api/v1/kpis: KPIs globales o filtrados.

GET /api/v1/analisis-factores: Análisis predictivo (Odds Ratios).

Autor

Klever Sandro Robalino Guamán

Carrera de Ingeniería en Sistemas de Información

Universidad Central del Ecuador
