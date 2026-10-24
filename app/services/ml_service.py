import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

# Variables categóricas que entran al modelo
VARIABLES = ["canal", "categoria", "agente", "segmento"]


def analizar_df(df: pd.DataFrame) -> dict:
    """Explica qué factores se asocian al incumplimiento del SLA sobre tickets limpios."""
    d = df[df["incumple_sla"].notna()].copy()
    d["incumple_sla"] = d["incumple_sla"].astype(int)
    if len(d) < 50:
        return {"error": "No hay suficientes datos para el análisis (mínimo 50 tickets)."}
    d["segmento"] = d["segmento"].fillna("Sin clasificar")

    # Tasa de incumplimiento por grupo
    tasas = {
        v: (d.groupby(v)["incumple_sla"].mean() * 100)
        .round(1)
        .sort_values(ascending=False)
        .to_dict()
        for v in VARIABLES
    }

    # Regresión logística con variables categóricas en one-hot.
    # La categoría de referencia es la más frecuente de cada variable.
    base = {v: d[v].value_counts().idxmax() for v in VARIABLES}
    X = pd.get_dummies(d[VARIABLES]).astype(float)
    X = X.drop(columns=[f"{v}_{b}" for v, b in base.items()])
    y = d["incumple_sla"]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    modelo = LogisticRegression(C=1e6, max_iter=2000).fit(X_tr, y_tr)
    auc = roc_auc_score(y_te, modelo.predict_proba(X_te)[:, 1])
    exactitud = modelo.score(X_te, y_te)

    factores = []
    for nombre, coef in zip(X.columns, modelo.coef_[0]):
        variable, categoria = nombre.split("_", 1)
        factores.append(
            {
                "variable": variable,
                "categoria": categoria,
                "odds_ratio": round(float(np.exp(coef)), 2),
                "efecto": "aumenta el riesgo" if coef > 0 else "reduce el riesgo",
            }
        )
    factores.sort(key=lambda f: abs(np.log(f["odds_ratio"])), reverse=True)

    # Relación entre incumplimiento y satisfacción
    con_sat = d[d["satisfaccion"].notna()]
    sat = {}
    if len(con_sat) > 10 and con_sat["incumple_sla"].nunique() == 2:
        sat = {
            "satisfaccion_si_cumple": round(
                float(con_sat[con_sat.incumple_sla == 0]["satisfaccion"].mean()), 2
            ),
            "satisfaccion_si_incumple": round(
                float(con_sat[con_sat.incumple_sla == 1]["satisfaccion"].mean()), 2
            ),
            "correlacion": round(
                float(con_sat["incumple_sla"].corr(con_sat["satisfaccion"])), 3
            ),
        }

    return {
        "tickets_analizados": len(d),
        "tasa_incumplimiento_global": round(float(y.mean() * 100), 1),
        "categorias_de_referencia": base,
        "factores": factores,
        "tasas_por_grupo": tasas,
        "relacion_satisfaccion": sat,
        "calidad_modelo": {
            "auc": round(float(auc), 3),
            "exactitud": round(float(exactitud), 3),
        },
        "interpretacion": (
            "Un odds ratio mayor que 1 indica que esa categoría tiene más riesgo de incumplir "
            "el SLA que la categoría de referencia; menor que 1, menos riesgo. "
            "No se incluye 'reabierto' como factor porque ocurre después del incumplimiento."
        ),
    }


def analizar_factores_incumplimiento(db: Session) -> dict:
    """Carga los tickets limpios desde la base y ejecuta el análisis de factores."""
    from app.models import TicketLimpio

    filas = db.query(TicketLimpio).all()
    df = pd.DataFrame(
        [
            {
                "canal": t.canal,
                "categoria": t.categoria,
                "agente": t.agente,
                "segmento": t.segmento,
                "satisfaccion": t.satisfaccion,
                "incumple_sla": t.incumple_sla,
            }
            for t in filas
        ]
    )
    if df.empty:
        return {"error": "No hay datos limpios. Ejecuta primero el ETL."}
    return analizar_df(df)