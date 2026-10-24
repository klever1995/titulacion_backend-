import re
import unicodedata

import numpy as np
import pandas as pd

# Catálogos: clave normalizada (minúsculas, sin tildes) -> valor oficial
CATEGORIAS = {
    "soporte tecnico": "Soporte técnico", "soporte": "Soporte técnico",
    "facturacion": "Facturación", "fact.": "Facturación", "fact": "Facturación",
    "ventas": "Ventas", "venta": "Ventas",
    "reclamos": "Reclamos", "reclamo": "Reclamos",
    "instalacion": "Instalación",
}
CANALES = {
    "correo": "Correo", "email": "Correo",
    "telefono": "Teléfono", "llamada": "Teléfono",
    "portal": "Portal", "web": "Portal",
    "chat": "Chat", "chat en linea": "Chat",
}
ESTADOS = {
    "cerrado": "Cerrado", "resuelto": "Cerrado",
    "abierto": "Abierto", "pendiente": "Abierto",
    "escalado": "Escalado", "escalado nivel 2": "Escalado",
}
SEGMENTOS = {"corporativo": "Corporativo", "personal": "Personal", "pyme": "Pyme"}

# Conjuntos de valores oficiales para validar contra los catálogos
CATEGORIAS_OFICIALES = set(CATEGORIAS.values())
CANALES_OFICIALES = set(CANALES.values())
ESTADOS_OFICIALES = set(ESTADOS.values())
SEGMENTOS_OFICIALES = set(SEGMENTOS.values())

# Formatos de fecha aceptados; se prueban en orden
FORMATOS_FECHA = [
    "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%d", "%d/%m/%Y",
]

# Expresiones regulares de validación
REGEX_ID = r"C\d{4}"
REGEX_FECHA_ISO = r"\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?"


def es_nulo(x) -> bool:
    """Indica si un valor debe tratarse como nulo (None, NaN o cadena vacía)."""
    if x is None:
        return True
    if isinstance(x, float) and np.isnan(x):
        return True
    return pd.isna(x) or str(x).strip() == ""


def sin_tilde(s: str) -> str:
    """Quita las tildes de un texto."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def clave(x):
    """Texto en minúsculas, sin tildes y sin espacios sobrantes (None si es nulo)."""
    if es_nulo(x):
        return None
    return sin_tilde(str(x)).strip().lower()


def mapear(serie: pd.Series, catalogo: dict) -> pd.Series:
    """Lleva cada valor al nombre oficial del catálogo; lo desconocido queda nulo."""
    return serie.map(lambda v: catalogo.get(clave(v)))


def normalizar_id(x):
    """' c-0123 ' -> 'C0123'; '123' -> 'C0123'; formato inválido o nulo -> None."""
    if es_nulo(x):
        return None
    s = re.sub(r"[\s\-]", "", str(x)).upper()
    if s in {"NONE", "NAN", "NULL"}:
        return None
    if s.isdigit():
        s = "C" + s.zfill(4)
    return s if re.fullmatch(REGEX_ID, s) else None


def normalizar_agente(x):
    """Devuelve el agente en formato 'Agente X' o 'Sin asignar' si no es válido."""
    if es_nulo(x):
        return "Sin asignar"
    s = clave(x).replace("_", " ").title()
    return s if re.fullmatch(r"Agente [A-Z]", s) else "Sin asignar"


def parsear_fechas(serie: pd.Series) -> pd.Series:
    """Convierte texto con varios formatos a fecha; con '/' se asume día/mes/año."""
    if pd.api.types.is_datetime64_any_dtype(serie):
        return serie
    s = serie.astype("string").str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for formato in FORMATOS_FECHA:
        intento = pd.to_datetime(s, format=formato, errors="coerce")
        out = out.fillna(intento.astype("datetime64[ns]"))
    return out


def a_booleano(serie: pd.Series) -> pd.Series:
    """Convierte 1/0, sí/no y true/false en booleanos; lo desconocido queda nulo."""
    valores = {
        "1": True, "si": True, "true": True,
        "0": False, "no": False, "false": False,
    }
    return serie.map(lambda v: valores.get(clave(v)) if clave(v) is not None else None)