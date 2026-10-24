import pandas as pd

from app.services.reglas import (
    CANALES_OFICIALES,
    CATEGORIAS_OFICIALES,
    ESTADOS_OFICIALES,
    REGEX_FECHA_ISO,
    REGEX_ID,
    SEGMENTOS_OFICIALES,
    clave,
    es_nulo,
    parsear_fechas,
)

# Dimensiones de calidad evaluadas en cada fuente
DIMENSIONES = ["completitud", "unicidad", "consistencia", "validez"]


def _fila(fuente, dimension, regla, etapa, evaluados, errores):
    """Construye el resultado de una regla con su puntaje de cumplimiento."""
    evaluados, errores = int(evaluados), int(errores)
    puntaje = round(100 * (1 - errores / evaluados), 2) if evaluados else 100.0
    return {
        "fuente": fuente,
        "dimension": dimension,
        "regla": regla,
        "etapa": etapa,
        "registros_evaluados": evaluados,
        "registros_con_error": errores,
        "puntaje": puntaje,
    }


def _informado(s: pd.Series) -> pd.Series:
    """Máscara de valores informados (no nulos)."""
    return ~s.map(es_nulo)


def _fuera_catalogo(s: pd.Series, oficiales: set):
    """Cuenta valores informados y cuántos no pertenecen al catálogo oficial."""
    t = s[_informado(s)]
    return len(t), int((~t.isin(oficiales)).sum())


def _formato_iso(s: pd.Series):
    """Cuenta valores informados y cuántos no cumplen el formato ISO."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return int(s.notna().sum()), 0
    t = s[_informado(s)].astype(str)
    return len(t), int((~t.str.fullmatch(REGEX_FECHA_ISO)).sum())


def evaluar_calidad(crm, tickets, encuestas, ids_crm: set, etapa: str, corte=None):
    """Evalúa las reglas de calidad sobre las tres fuentes y devuelve una lista de resultados."""
    f = []

    # Tickets
    t = tickets
    est = t["estado"].map(clave)
    abierto = est.isin(["abierto", "pendiente"])
    ap, ci = parsear_fechas(t["fecha_apertura"]), parsear_fechas(t["fecha_cierre"])
    if corte is None:
        corte = ap.max() + pd.Timedelta(days=30)

    f.append(_fila("tickets", "completitud", "id_cliente informado", etapa,
                   len(t), (~_informado(t["id_cliente"])).sum()))
    f.append(_fila("tickets", "completitud", "agente asignado", etapa,
                   len(t), (~_informado(t["agente"])).sum()
                   + (t["agente"].astype(str) == "Sin asignar").sum()))
    sla = pd.to_numeric(t["sla_objetivo_horas"], errors="coerce")
    f.append(_fila("tickets", "completitud", "sla_objetivo_horas informado", etapa,
                   len(t), sla.isna().sum()))
    f.append(_fila("tickets", "completitud", "fecha_cierre informada en tickets no abiertos", etapa,
                   (~abierto).sum(), (~abierto & ci.isna()).sum()))

    f.append(_fila("tickets", "unicidad", "id_ticket sin repetir", etapa,
                   len(t), t["id_ticket"].duplicated().sum()))

    ids = t["id_cliente"][_informado(t["id_cliente"])].astype(str)
    f.append(_fila("tickets", "consistencia", "id_cliente con formato C####", etapa,
                   len(ids), (~ids.str.fullmatch(REGEX_ID)).sum()))
    for col, oficiales, nombre in [
        ("categoria", CATEGORIAS_OFICIALES, "categoría"),
        ("canal", CANALES_OFICIALES, "canal"),
        ("estado", ESTADOS_OFICIALES, "estado"),
    ]:
        n, e = _fuera_catalogo(t[col], oficiales)
        f.append(_fila("tickets", "consistencia", f"{nombre} igual al catálogo oficial", etapa, n, e))
    for col in ["fecha_apertura", "fecha_cierre"]:
        n, e = _formato_iso(t[col])
        f.append(_fila("tickets", "consistencia", f"{col} en un solo formato", etapa, n, e))
    f.append(_fila("tickets", "consistencia", "ticket abierto no debe tener fecha de cierre", etapa,
                   abierto.sum(), (abierto & ci.notna()).sum()))

    ok = ci.notna() & ap.notna()
    f.append(_fila("tickets", "validez", "cierre no anterior a la apertura", etapa,
                   ok.sum(), (ci[ok] < ap[ok]).sum()))
    f.append(_fila("tickets", "validez", "cierre no posterior a la fecha de corte", etapa,
                   ci.notna().sum(), (ci > corte).sum()))
    f.append(_fila("tickets", "validez", "sla_objetivo_horas mayor que cero", etapa,
                   sla.notna().sum(), (sla <= 0).sum()))
    reab = t["reabierto"][_informado(t["reabierto"])].astype(str).str.strip().str.lower()
    f.append(_fila("tickets", "validez", "reabierto es 0/1", etapa,
                   len(reab), (~reab.isin(["0", "1", "true", "false"])).sum()))
    f.append(_fila("tickets", "validez", "id_cliente existe en el CRM", etapa,
                   len(ids), (~ids.isin(ids_crm)).sum()))

    # CRM
    c = crm
    f.append(_fila("crm", "completitud", "segmento informado", etapa,
                   len(c), (~_informado(c["segmento"])).sum()
                   + (c["segmento"].astype(str) == "Sin clasificar").sum()))
    f.append(_fila("crm", "completitud", "ciudad informada", etapa,
                   len(c), (~_informado(c["ciudad"])).sum()))
    f.append(_fila("crm", "unicidad", "id_cliente sin repetir", etapa,
                   len(c), c["id_cliente"].duplicated().sum()))
    n, e = _fuera_catalogo(c["segmento"], SEGMENTOS_OFICIALES | {"Sin clasificar"})
    f.append(_fila("crm", "consistencia", "segmento igual al catálogo oficial", etapa, n, e))
    n, e = _formato_iso(c["fecha_alta"])
    f.append(_fila("crm", "consistencia", "fecha_alta en un solo formato", etapa, n, e))
    alta = parsear_fechas(c["fecha_alta"])
    con_alta = _informado(c["fecha_alta"])
    f.append(_fila("crm", "validez", "fecha_alta es una fecha válida y no futura", etapa,
                   con_alta.sum(), (con_alta & (alta.isna() | (alta > corte))).sum()))

    # Encuestas
    s = encuestas
    f.append(_fila("encuestas", "completitud", "id_ticket informado", etapa,
                   len(s), (~_informado(s["id_ticket"])).sum()))
    f.append(_fila("encuestas", "completitud", "satisfaccion informada", etapa,
                   len(s), (~_informado(s["satisfaccion"])).sum()))
    con_ticket = s["id_ticket"][_informado(s["id_ticket"])]
    f.append(_fila("encuestas", "unicidad", "una encuesta por ticket", etapa,
                   len(con_ticket), con_ticket.duplicated().sum()))
    ids_formato = s["id_cliente"][_informado(s["id_cliente"])].astype(str)
    f.append(_fila("encuestas", "consistencia", "id_cliente con formato C####", etapa,
                   len(ids_formato), (~ids_formato.str.fullmatch(REGEX_ID)).sum()))
    n, e = _formato_iso(s["fecha_respuesta"])
    f.append(_fila("encuestas", "consistencia", "fecha_respuesta en un solo formato", etapa, n, e))
    sat = pd.to_numeric(s["satisfaccion"], errors="coerce")
    f.append(_fila("encuestas", "validez", "satisfaccion entre 1 y 5", etapa,
                   sat.notna().sum(), ((sat < 1) | (sat > 5)).sum()))
    ids_e = s["id_cliente"][_informado(s["id_cliente"])].astype(str)
    f.append(_fila("encuestas", "validez", "id_cliente existe en el CRM", etapa,
                   len(ids_e), (~ids_e.isin(ids_crm)).sum()))
    return f


def resumir(filas: list) -> dict:
    """Promedia las reglas por dimensión y calcula el puntaje total."""
    df = pd.DataFrame(filas)
    out = {d: round(float(df[df["dimension"] == d]["puntaje"].mean()), 2) for d in DIMENSIONES}
    out["total"] = round(sum(out.values()) / len(DIMENSIONES), 2)
    return out