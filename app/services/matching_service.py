import pandas as pd

from app.services.reglas import es_nulo, normalizar_id


def _vecinos(id_cliente: str) -> set:
    """IDs a distancia uno: un par de dígitos intercambiados o un dígito distinto."""
    prefijo, digitos = id_cliente[0], id_cliente[1:]
    out = set()
    for i in range(len(digitos) - 1):
        d = list(digitos)
        d[i], d[i + 1] = d[i + 1], d[i]
        out.add(prefijo + "".join(d))
    for i in range(len(digitos)):
        for n in "0123456789":
            if n != digitos[i]:
                out.add(prefijo + digitos[:i] + n + digitos[i + 1:])
        out.add(prefijo + digitos[:i] + n + digitos[i + 1:])
    out.discard(id_cliente)
    return out


def emparejar_cliente(crudo, ids_crm: set):
    """Empareja un id_cliente con el CRM por niveles y devuelve (id_final, metodo, motivo, candidato)."""
    if es_nulo(crudo):
        return None, "sin_match", "id_cliente nulo", None
    canon = normalizar_id(crudo)
    if canon is None:
        return None, "sin_match", "formato de id_cliente inválido", None
    if canon in ids_crm:
        metodo = "exacto" if str(crudo) == canon else "normalizado"
        return canon, metodo, None, None
    candidatos = sorted(_vecinos(canon) & ids_crm)
    if len(candidatos) == 1:
        return candidatos[0], "aproximado", None, candidatos[0]
    if len(candidatos) > 1:
        return None, "sin_match", "ambiguo: varios clientes similares", ",".join(candidatos[:5])
    return None, "sin_match", "cliente no existe en el CRM", None


def emparejar_serie(serie: pd.Series, ids_crm: set) -> pd.DataFrame:
    """Aplica el emparejamiento a una columna y devuelve el resultado por fila."""
    res = serie.map(lambda v: emparejar_cliente(v, ids_crm))
    return pd.DataFrame(
        res.tolist(),
        index=serie.index,
        columns=["id_final", "metodo", "motivo", "candidato"],
    )