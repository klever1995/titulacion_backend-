import re

import pandas as pd

from app.services.reglas import es_nulo
from app.services.quality_service import evaluar_calidad


def _patron_id(x) -> str:
    """Clasifica un id_cliente según su formato."""
    if es_nulo(x):
        return "nulo"
    s = str(x)
    if s != s.strip():
        return "con espacios"
    if "-" in s:
        return "con guion"
    if re.fullmatch(r"C\d{4}", s):
        return "formato correcto"
    if re.fullmatch(r"c\d{4}", s):
        return "minúsculas"
    if re.fullmatch(r"\d{4}", s):
        return "sin prefijo C"
    return "otro formato"


def _patron_fecha(x) -> str:
    """Clasifica una fecha según el formato con el que llegó."""
    if es_nulo(x):
        return "nulo"
    s = str(x).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", s):
        return "AAAA-MM-DD HH:MM"
    if re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", s):
        return "DD/MM/AAAA HH:MM"
    if re.fullmatch(r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}", s):
        return "AAAA/MM/DD HH:MM:SS"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return "AAAA-MM-DD"
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", s):
        return "DD/MM/AAAA"
    return "otro formato"


def _columnas(df: pd.DataFrame) -> list:
    """Resume nulos y valores distintos por columna."""
    return [
        {
            "columna": c,
            "nulos": int(df[c].map(es_nulo).sum()),
            "porcentaje_nulos": round(100 * df[c].map(es_nulo).mean(), 2),
            "valores_distintos": int(df[c].nunique(dropna=True)),
        }
        for c in df.columns
    ]


def perfilar_fuentes(crm: pd.DataFrame, tickets: pd.DataFrame, encuestas: pd.DataFrame) -> dict:
    """Describe los problemas de las tres fuentes crudas sin corregirlos."""
    ids_crm = set(crm["id_cliente"].dropna().astype(str).str.strip())
    reglas = evaluar_calidad(crm, tickets, encuestas, ids_crm, "antes")

    def reglas_de(fuente):
        return [r for r in reglas if r["fuente"] == fuente]

    return {
        "crm": {
            "filas": len(crm),
            "duplicados_por_id": int(crm["id_cliente"].duplicated().sum()),
            "columnas": _columnas(crm),
            "formatos_fecha_alta": crm["fecha_alta"].map(_patron_fecha).value_counts().to_dict(),
            "segmentos_distintos": crm["segmento"].fillna("(nulo)").value_counts().to_dict(),
            "reglas": reglas_de("crm"),
        },
        "tickets": {
            "filas": len(tickets),
            "duplicados_por_id": int(tickets["id_ticket"].duplicated().sum()),
            "columnas": _columnas(tickets),
            "patrones_id_cliente": tickets["id_cliente"].map(_patron_id).value_counts().to_dict(),
            "formatos_fecha_apertura": tickets["fecha_apertura"].map(_patron_fecha).value_counts().to_dict(),
            "formatos_fecha_cierre": tickets["fecha_cierre"].map(_patron_fecha).value_counts().to_dict(),
            "variantes_categoria": int(tickets["categoria"].nunique()),
            "variantes_canal": int(tickets["canal"].nunique()),
            "variantes_estado": int(tickets["estado"].nunique()),
            "variantes_agente": int(tickets["agente"].nunique()),
            "reglas": reglas_de("tickets"),
        },
        "encuestas": {
            "filas": len(encuestas),
            "duplicados_por_ticket": int(encuestas["id_ticket"].dropna().duplicated().sum()),
            "columnas": _columnas(encuestas),
            "patrones_id_cliente": encuestas["id_cliente"].map(_patron_id).value_counts().to_dict(),
            "reglas": reglas_de("encuestas"),
        },
    }