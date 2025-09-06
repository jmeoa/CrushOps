# utils.py — hardened
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO

PAL = ["#328BA1", "#0B5563", "#00AFAA", "#66C7C7", "#BFD8D2"]
sns.set_theme(style="whitegrid", palette=PAL)

EXPECTED = {
    "Fecha": ["fecha", "date"],
    "mineral_procesado_real_t": ["mineral_procesado_real_t", "ton_real", "tons_real", "mineral_real_t"],
    "rendimiento_real_tph": ["rendimiento_real_tph", "tph_real", "real_tph"],
    "tiempo_operativo_real_h/dia": ["tiempo_operativo_real_h/dia", "horas_reales", "horas_real_h_dia", "h_real"],
    "mineral_procesado_plan_t": ["mineral_procesado_plan_t", "ton_plan", "tons_plan", "mineral_plan_t"],
    "rendimiento_plan_tph": ["rendimiento_plan_tph", "tph_plan", "plan_tph"],
    "tiempo_operativo_plan_h/dia": ["tiempo_operativo_plan_h/dia", "horas_plan", "h_plan"]
}

def get_template_csv() -> str:
    return (
        "Fecha,mineral_procesado_real_t,rendimiento_real_tph,tiempo_operativo_real_h/dia,"
        "mineral_procesado_plan_t,rendimiento_plan_tph,tiempo_operativo_plan_h/dia\n"
        "2025-01-01,40,2,20,41,2.1,19.5\n"
        "2025-01-02,38,1.9,20,41,2.1,19.5\n"
    )

def _normalize_colname(c: str) -> str:
    return (
        c.strip().lower()
         .replace(" ", "_")
         .replace("__","_")
    )

def _map_columns(df_cols):
    norm = {_normalize_colname(c): c for c in df_cols}
    mapping = {}
    for std, aliases in EXPECTED.items():
        found = None
        for a in aliases:
            if a in norm:
                found = norm[a]; break
        if not found:
            # intento exacto por nombre std normalizado
            k = _normalize_colname(std)
            if k in norm: found = norm[k]
        mapping[std] = found
    missing = [k for k,v in mapping.items() if v is None]
    if missing:
        raise ValueError(f"Columnas faltantes o no reconocidas: {missing}")
    return mapping

def _to_numeric(series: pd.Series) -> pd.Series:
    # Convierte "2,100" -> 2100, "  " -> NaN
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce")

def load_dataset(file):
    raw = file.read().decode("utf-8", errors="ignore")
    try:
        df = pd.read_csv(StringIO(raw))
    except Exception:
        df = pd.read_csv(StringIO(raw), sep=";")

    mapping = _map_columns(df.columns)

    out = pd.DataFrame()
    out["Fecha"] = pd.to_datetime(df[mapping["Fecha"]], errors="coerce", dayfirst=False)
    out["mineral_procesado_real_t"] = _to_numeric(df[mapping["mineral_procesado_real_t"]])
    out["rendimiento_real_tph"] = _to_numeric(df[mapping["rendimiento_real_tph"]])
    out["tiempo_operativo_real_h/dia"] = _to_numeric(df[mapping["tiempo_operativo_real_h/dia"]])
    out["mineral_procesado_plan_t"] = _to_numeric(df[mapping["mineral_procesado_plan_t"]])
    out["rendimiento_plan_tph"] = _to_numeric(df[mapping["rendimiento_plan_tph"]])
    out["tiempo_operativo_plan_h/dia"] = _to_numeric(df[mapping["tiempo_operativo_plan_h/dia"]])

    out = out.dropna(subset=["Fecha"]).sort_values("Fecha").reset_index(drop=True)

    info = {
        "mapeo_columnas": mapping,
        "filas": int(len(out)),
        "rango_fechas": [str(out["Fecha"].min()), str(out["Fecha"].max())],
        "tipos": {c: str(out[c].dtype) for c in out.columns}
    }
    return out, info

def _numeric_guard(df: pd.DataFrame) -> pd.DataFrame:
    # Asegura que las columnas numéricas sigan siendo numéricas (por si el usuario trae df sin pasar por load_dataset)
    num_cols = [c for c in df.columns if c != "Fecha"]
    g = df.copy()
    for c in num_cols:
        g[c] = _to_numeric(g[c])
    if "Fecha" in g.columns:
        g["Fecha"] = pd.to_datetime(g["Fecha"], errors="coerce")
        g = g.dropna(subset=["Fecha"]).sort_values("Fecha").reset_index(drop=True)
    return g

def calcular_kpis(df: pd.DataFrame) -> pd.DataFrame:
    # Blindado: convierte a numérico siempre
    df = _numeric_guard(df)
    resumen = {
        "Mineral procesado real (t)": df["mineral_procesado_real_t"].sum(),
        "Mineral planificado (t)": df["mineral_procesado_plan_t"].sum(),
        "TPH real promedio": df["rendimiento_real_tph"].mean(),
        "TPH plan promedio": df["rendimiento_plan_tph"].mean(),
        "Horas reales promedio": df["tiempo_operativo_real_h/dia"].mean(),
        "Horas plan promedio": df["tiempo_operativo_plan_h/dia"].mean()
    }
    return pd.DataFrame.from_dict(resumen, orient="index", columns=["Valor"])

def graficos_quickcrush(df: pd.DataFrame):
    df = _numeric_guard(df)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    sns.lineplot(data=df, x="Fecha", y="rendimiento_real_tph",
                 ax=axes[0], label="TPH Real", color=PAL[0])
    sns.lineplot(data=df, x="Fecha", y="rendimiento_plan_tph",
                 ax=axes[0], label="TPH Plan", color="grey", linestyle="--")
    axes[0].set_title("Evolución TPH (real vs plan)")
    axes[0].set_xlabel("Fecha"); axes[0].set_ylabel("TPH")
    axes[0].tick_params(axis="x", rotation=25)

    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_real_h/dia",
                 ax=axes[1], label="Horas Reales", color=PAL[2])
    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_plan_h/dia",
                 ax=axes[1], label="Horas Plan", color="grey", linestyle="--")
    axes[1].set_title("Disponibilidad (horas/día) real vs plan")
    axes[1].set_xlabel("Fecha"); axes[1].set_ylabel("Horas/día")
    axes[1].tick_params(axis="x", rotation=25)

    fig.tight_layout()
    return fig
