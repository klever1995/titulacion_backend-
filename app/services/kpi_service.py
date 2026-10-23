# ==============================
# app/services/kpi_service.py
# Cálculo de KPIs con filtros (sin base de datos, fácil de probar)
# ==============================
import pandas as pd

COLUMNAS = [
    "id_ticket", "id_cliente", "fecha_apertura", "fecha_cierre", "categoria", "canal",
    "estado", "agente", "reabierto", "sla_objetivo_horas", "segmento", "satisfaccion",
    "tiempo_resolucion_horas", "incumple_sla",
]
AGRUPABLES = ["categoria", "canal", "agente", "segmento", "estado", "mes"]


def filtrar(df: pd.DataFrame, categoria=None, canal=None, agente=None, segmento=None,
            desde=None, hasta=None) -> pd.DataFrame:
    for columna, valor in [("categoria", categoria), ("canal", canal),
                           ("agente", agente), ("segmento", segmento)]:
        if valor:
            df = df[df[columna] == valor]
    if desde is not None:
        df = df[df["fecha_apertura"] >= pd.Timestamp(desde)]
    if hasta is not None:
        df = df[df["fecha_apertura"] < pd.Timestamp(hasta) + pd.Timedelta(days=1)]
    return df


def _promedio(serie: pd.Series) -> float:
    valor = serie.mean()
    return 0.0 if pd.isna(valor) else round(float(valor), 2)


def calcular_kpis(df: pd.DataFrame) -> dict:
    """KPIs sobre un conjunto de tickets. Cada KPI usa solo los tickets donde tiene sentido."""
    total = len(df)
    if total == 0:
        return {"total_tickets": 0, "tiempo_promedio": 0.0, "satisfaccion_promedio": 0.0,
                "reincidencia": 0.0, "cumplimiento_sla": 0.0, "tasa_escalamiento": 0.0,
                "backlog": 0}
    medidos = df[df["incumple_sla"].notna()]          # tickets con resultado de SLA conocido
    cumplen = (medidos["incumple_sla"].astype(float) == 0).sum()
    return {
        "total_tickets": int(total),
        "tiempo_promedio": _promedio(df["tiempo_resolucion_horas"]),
        "satisfaccion_promedio": _promedio(df["satisfaccion"]),
        "reincidencia": round(float(df["reabierto"].astype(float).mean() * 100), 2),
        "cumplimiento_sla": round(float(cumplen / len(medidos) * 100), 2) if len(medidos) else 0.0,
        "tasa_escalamiento": round(float((df["estado"] == "Escalado").mean() * 100), 2),
        "backlog": int((df["estado"] == "Abierto").sum()),
    }


def kpis_por_grupo(df: pd.DataFrame, columna: str) -> list:
    if columna == "mes":
        df = df.assign(mes=df["fecha_apertura"].dt.strftime("%Y-%m").fillna("Sin fecha"))
    return [{columna: str(valor), **calcular_kpis(grupo)}
            for valor, grupo in df.groupby(columna, dropna=False)]