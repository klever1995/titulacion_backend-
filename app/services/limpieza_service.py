import numpy as np
import pandas as pd

from app.services.matching_service import emparejar_serie
from app.services.reglas import (
    CANALES,
    CATEGORIAS,
    ESTADOS,
    SEGMENTOS,
    a_booleano,
    es_nulo,
    mapear,
    normalizar_agente,
    parsear_fechas,
)


def _cuarentena(fuente, ids, valores, motivo, candidatos=None):
    """Construye filas de cuarentena a partir de tres series alineadas."""
    ids = list(ids)
    valores = list(valores)
    candidatos = list(candidatos) if candidatos is not None else [None] * len(ids)
    return [
        {
            "fuente": fuente,
            "id_registro": None if es_nulo(i) else str(i),
            "valor_original": None if es_nulo(v) else str(v),
            "motivo": motivo,
            "candidato": c,
        }
        for i, v, c in zip(ids, valores, candidatos)
    ]


def limpiar_crm(raw: pd.DataFrame):
    """Normaliza el CRM y resuelve duplicados y nulos de segmento."""
    q = []
    df = raw.copy()
    df["id_cliente"] = df["id_cliente"].astype("string").str.strip().str.upper()
    df["segmento"] = mapear(df["segmento"], SEGMENTOS)
    df["ciudad"] = df["ciudad"].map(lambda v: None if es_nulo(v) else str(v).strip().title())
    df["fecha_alta"] = parsear_fechas(df["fecha_alta"])

    # Si un cliente repetido tiene segmentos distintos no hay forma de saber cuál es el correcto
    conflictos = (
        df.groupby("id_cliente")["segmento"]
        .apply(lambda s: s.dropna().nunique() > 1)
    )
    ids_conflicto = set(conflictos[conflictos].index)
    df = df.drop_duplicates(subset=["id_cliente", "segmento", "ciudad", "fecha_alta"])
    df = df.drop_duplicates(subset=["id_cliente"], keep="first").copy()
    enc = df["id_cliente"].isin(ids_conflicto)
    df.loc[enc, "segmento"] = None
    q += _cuarentena(
        "crm",
        df.loc[enc, "id_cliente"],
        df.loc[enc, "id_cliente"],
        "cliente repetido con segmentos distintos",
    )
    sin_seg = df["segmento"].isna() & ~enc
    q += _cuarentena(
        "crm",
        df.loc[sin_seg, "id_cliente"],
        [None] * int(sin_seg.sum()),
        "segmento faltante en el CRM",
    )
    df["segmento"] = df["segmento"].fillna("Sin clasificar")
    return df.reset_index(drop=True), q


def limpiar_tickets(raw: pd.DataFrame, ids_crm: set, segmentos: pd.DataFrame):
    """Normaliza los tickets, resuelve duplicados y calcula métricas por ticket."""
    q = []
    df = raw.copy()
    df["id_ticket"] = df["id_ticket"].astype("string").str.strip().str.upper()

    df = df.drop_duplicates().copy()

    df["categoria"] = mapear(df["categoria"], CATEGORIAS)
    df["canal"] = mapear(df["canal"], CANALES)
    df["estado"] = mapear(df["estado"], ESTADOS)
    df["agente"] = df["agente"].map(normalizar_agente)
    df["reabierto"] = a_booleano(df["reabierto"])
    df["sla_objetivo_horas"] = pd.to_numeric(df["sla_objetivo_horas"], errors="coerce")
    df["fecha_apertura"] = parsear_fechas(df["fecha_apertura"])
    df["fecha_cierre"] = parsear_fechas(df["fecha_cierre"])

    # Ante un id_ticket repetido con datos distintos, se prefiere la fila cuyo estado
    # es coherente con la fecha de cierre
    repetido = df["id_ticket"].duplicated(keep=False)
    coherente = ((df["estado"] == "Abierto") == df["fecha_cierre"].isna()).astype(int)
    df = (
        df.assign(_c=coherente)
        .sort_values("_c", ascending=False, kind="stable")
        .drop_duplicates(subset=["id_ticket"], keep="first")
        .drop(columns="_c")
    )
    q += _cuarentena(
        "tickets",
        df.loc[repetido.reindex(df.index, fill_value=False), "id_ticket"],
        [None] * int(repetido.reindex(df.index, fill_value=False).sum()),
        "mismo id_ticket con datos distintos (se conservó una versión)",
    )
    df = df.sort_values("id_ticket").reset_index(drop=True)

    # Un SLA inválido o faltante se imputa con el valor más frecuente de su categoría
    valido = df["sla_objetivo_horas"].where(df["sla_objetivo_horas"] > 0)
    moda = valido.groupby(df["categoria"]).agg(
        lambda s: s.mode().iloc[0] if s.notna().any() else np.nan
    )
    falta = valido.isna()
    df["sla_objetivo_horas"] = valido.fillna(df["categoria"].map(moda))
    q += _cuarentena(
        "tickets",
        df.loc[falta, "id_ticket"],
        [None] * int(falta.sum()),
        "sla_objetivo_horas faltante o inválido (imputado por categoría)",
    )

    # Incoherencias entre estado y fechas
    corte = df["fecha_apertura"].max() + pd.Timedelta(days=30)
    abierto_con_cierre = (df["estado"] == "Abierto") & df["fecha_cierre"].notna()
    cierre_antes = df["fecha_cierre"] < df["fecha_apertura"]
    cierre_futuro = df["fecha_cierre"] > corte
    cerrado_sin_cierre = (df["estado"].isin(["Cerrado", "Escalado"])) & df["fecha_cierre"].isna()
    for mascara, motivo in [
        (abierto_con_cierre, "ticket abierto con fecha de cierre (se ignoró el cierre)"),
        (cierre_antes, "fecha de cierre anterior a la apertura"),
        (cierre_futuro, "fecha de cierre en el futuro"),
        (cerrado_sin_cierre, "ticket cerrado sin fecha de cierre"),
    ]:
        q += _cuarentena(
            "tickets",
            df.loc[mascara, "id_ticket"],
            [None] * int(mascara.sum()),
            motivo,
        )
    df.loc[abierto_con_cierre | cierre_antes | cierre_futuro, "fecha_cierre"] = pd.NaT

    # Emparejamiento de clientes por niveles (exacto, normalizado, aproximado)
    m = emparejar_serie(df["id_cliente"], ids_crm)
    sin = m["id_final"].isna()
    filas = _cuarentena(
        "tickets",
        df.loc[sin, "id_ticket"],
        df.loc[sin, "id_cliente"],
        "",
        m.loc[sin, "candidato"],
    )
    for fila, motivo in zip(filas, m.loc[sin, "motivo"]):
        fila["motivo"] = "id_cliente: " + motivo
    q += filas
    df["id_cliente"] = m["id_final"]
    df["metodo_match"] = m["metodo"]
    df = df.merge(segmentos[["id_cliente", "segmento"]], on="id_cliente", how="left")

    # Métricas calculadas: solo se rellenan cuando hay datos válidos, nunca con 0
    horas = (df["fecha_cierre"] - df["fecha_apertura"]).dt.total_seconds() / 3600
    df["tiempo_resolucion_horas"] = horas.where(df["estado"] != "Abierto").round(2)
    df["incumple_sla"] = (df["tiempo_resolucion_horas"] > df["sla_objetivo_horas"]).astype("object")
    df.loc[df["tiempo_resolucion_horas"].isna(), "incumple_sla"] = None
    df["reabierto"] = df["reabierto"].fillna(False).astype(bool)
    return df, q


def limpiar_encuestas(raw: pd.DataFrame, ids_crm: set, tickets_limpios: pd.DataFrame):
    """Normaliza las encuestas y las cruza con tickets y CRM."""
    q = []
    df = raw.copy().drop_duplicates()
    df["id_ticket"] = df["id_ticket"].astype("string").str.strip().str.upper()
    df["satisfaccion"] = pd.to_numeric(df["satisfaccion"], errors="coerce")
    df["fecha_respuesta"] = parsear_fechas(df["fecha_respuesta"])

    fuera = df["satisfaccion"].notna() & ~df["satisfaccion"].between(1, 5)
    q += _cuarentena(
        "encuestas",
        df.loc[fuera, "id_ticket"],
        df.loc[fuera, "satisfaccion"],
        "satisfaccion fuera del rango 1-5",
    )
    df.loc[fuera, "satisfaccion"] = np.nan
    falta = df["satisfaccion"].isna() & ~fuera
    q += _cuarentena(
        "encuestas",
        df.loc[falta, "id_ticket"],
        [None] * int(falta.sum()),
        "satisfaccion faltante",
    )

    sin_ticket = df["id_ticket"].isna()
    q += _cuarentena(
        "encuestas",
        df.loc[sin_ticket, "id_cliente"],
        df.loc[sin_ticket, "id_cliente"],
        "encuesta sin id_ticket (no se puede asociar a un ticket)",
    )
    df = df[~sin_ticket].drop_duplicates(subset=["id_ticket"], keep="first").copy()

    m = emparejar_serie(df["id_cliente"], ids_crm)
    sin = m["id_final"].isna()
    filas = _cuarentena(
        "encuestas",
        df.loc[sin, "id_ticket"],
        df.loc[sin, "id_cliente"],
        "",
        m.loc[sin, "candidato"],
    )
    for fila, motivo in zip(filas, m.loc[sin, "motivo"]):
        fila["motivo"] = "id_cliente de la encuesta: " + motivo
    q += filas
    df["id_cliente"] = m["id_final"]
    
    # NUEVO: Guardamos el método de emparejamiento en el DataFrame de encuestas
    df["metodo_match"] = m["metodo"]

    # Si el cliente de la encuesta no coincide con el del ticket, se registra en cuarentena
    cli_ticket = tickets_limpios.set_index("id_ticket")["id_cliente"]
    esperado = df["id_ticket"].map(cli_ticket)
    distinto = df["id_cliente"].notna() & esperado.notna() & (df["id_cliente"] != esperado)
    q += _cuarentena(
        "encuestas",
        df.loc[distinto, "id_ticket"],
        df.loc[distinto, "id_cliente"],
        "el cliente de la encuesta no coincide con el del ticket",
        esperado[distinto],
    )
    return df.reset_index(drop=True), q


def ejecutar_etl(crm_raw: pd.DataFrame, tickets_raw: pd.DataFrame, encuestas_raw: pd.DataFrame):
    """Limpia las tres fuentes y devuelve (crm, tickets, encuestas, cuarentena, resumen_match, resumen_match_encuestas)."""
    crm, q1 = limpiar_crm(crm_raw)
    ids_crm = set(crm["id_cliente"])
    tickets, q2 = limpiar_tickets(tickets_raw, ids_crm, crm)
    encuestas, q3 = limpiar_encuestas(encuestas_raw, ids_crm, tickets)

    sat = encuestas.set_index("id_ticket")["satisfaccion"]
    tickets["satisfaccion"] = tickets["id_ticket"].map(sat)
    resumen_match = tickets["metodo_match"].value_counts().to_dict()
    
    # NUEVO: Calculamos el resumen de emparejamiento de las encuestas
    resumen_match_encuestas = encuestas["metodo_match"].value_counts().to_dict()
    
    return crm, tickets, encuestas, q1 + q2 + q3, resumen_match, resumen_match_encuestas