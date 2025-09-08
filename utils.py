
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter, MonthLocator
import statsmodels.api as sm
import statsmodels.formula.api as smf
from io import StringIO

# Paleta profesional
PAL = ["#328BA1", "#0B5563", "#00AFAA", "#66C7C7", "#BFD8D2"]
sns.set_theme(style="whitegrid", palette=PAL)

EXPECTED = {
    "Fecha": ["fecha","date"],
    "mineral_procesado_real_t": ["mineral_procesado_real_t","ton_real","tons_real","mineral_real_t"],
    "rendimiento_real_tph": ["rendimiento_real_tph","tph_real","real_tph"],
    "tiempo_operativo_real_h/dia": ["tiempo_operativo_real_h/dia","horas_reales","horas_real_h_dia","h_real"],
    "mineral_procesado_plan_t": ["mineral_procesado_plan_t","ton_plan","tons_plan","mineral_plan_t"],
    "rendimiento_plan_tph": ["rendimiento_plan_tph","tph_plan","plan_tph"],
    "tiempo_operativo_plan_h/dia": ["tiempo_operativo_plan_h/dia","horas_plan","h_plan"]
}

def _normalize_colname(c: str) -> str:
    return c.strip().lower().replace("/", "_").replace(" ", "_")

def _map_columns(cols):
    norm = {_normalize_colname(c): c for c in cols}
    mapping = {}
    for std, aliases in EXPECTED.items():
        found = None
        for a in aliases + [_normalize_colname(std)]:
            if a in norm:
                found = norm[a]; break
        mapping[std] = found
    miss = [k for k,v in mapping.items() if v is None]
    if miss:
        raise ValueError(f"Faltan columnas requeridas: {miss}")
    return mapping

def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(".", "", regex=False).str.replace(",", "", regex=False).str.strip(), errors="coerce")

def load_dataset(uploaded_or_path):
    if hasattr(uploaded_or_path, "getvalue"):
        raw = uploaded_or_path.getvalue().decode("utf-8", errors="ignore")
        try:
            df = pd.read_csv(StringIO(raw))
        except Exception:
            df = pd.read_csv(StringIO(raw), sep=";")
    else:
        df = pd.read_csv(uploaded_or_path)
    mapping = _map_columns(df.columns)
    out = pd.DataFrame()
    out["Fecha"] = pd.to_datetime(df[mapping["Fecha"]], errors="coerce", dayfirst=True)
    for k in [k for k in EXPECTED.keys() if k!="Fecha"]:
        out[k] = _to_num(df[mapping[k]])
    out = out.dropna(subset=["Fecha"]).sort_values("Fecha").reset_index(drop=True)
    out["mes"] = out["Fecha"].dt.to_period("M").astype(str)
    return out

# ---------- KPIs ----------
def calcular_kpis(df: pd.DataFrame) -> pd.DataFrame:
    d = {
        "Mineral real (t)": df["mineral_procesado_real_t"].sum(),
        "Mineral plan (t)": df["mineral_procesado_plan_t"].sum(),
        "Δ Mineral (t)": df["mineral_procesado_real_t"].sum() - df["mineral_procesado_plan_t"].sum(),
        "TPH real prom": df["rendimiento_real_tph"].mean(),
        "TPH plan prom": df["rendimiento_plan_tph"].mean(),
        "Horas reales prom": df["tiempo_operativo_real_h/dia"].mean(),
        "Horas plan prom": df["tiempo_operativo_plan_h/dia"].mean(),
    }
    return pd.DataFrame({"KPI": d.keys(), "Valor": d.values()})

# ---------- Formateadores ----------
def miles(x, pos=None):
    return f"{int(x):,}".replace(",", ".")

def sin_dec(x, pos=None):
    try:
        return f"{int(round(x)):,}".replace(",", ".")
    except Exception:
        return ""

# ---------- Gráficos ----------
def evolucion_tph_horas(df: pd.DataFrame):
    fig, axes = plt.subplots(1,2, figsize=(16,5), sharex=True)
    # TPH
    sns.lineplot(data=df, x="Fecha", y="rendimiento_real_tph", label="TPH Real", ax=axes[0], linewidth=1.8, color=PAL[0])
    sns.lineplot(data=df, x="Fecha", y="rendimiento_plan_tph", label="TPH Plan", ax=axes[0], linewidth=1.8, color="grey", linestyle="--")
    axes[0].set_ylabel("TPH"); axes[0].legend(loc="upper left")
    # Horas
    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_real_h/dia", label="Horas Reales", ax=axes[1], linewidth=1.8, color=PAL[2])
    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_plan_h/dia", label="Horas Plan", ax=axes[1], linewidth=1.8, color="grey", linestyle="--")
    axes[1].set_ylabel("Horas/día"); axes[1].legend(loc="upper left")
    for ax in axes:
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter("%b-%y"))
        ax.yaxis.set_major_formatter(FuncFormatter(sin_dec))
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig

def barras_delta_prom(df: pd.DataFrame):
    # promedios y deltas
    medios = {
        "TPH": (df["rendimiento_real_tph"].mean(), df["rendimiento_plan_tph"].mean()),
        "Horas": (df["tiempo_operativo_real_h/dia"].mean(), df["tiempo_operativo_plan_h/dia"].mean())
    }
    fig, axes = plt.subplots(1,2, figsize=(14,5))
    # TPH
    real, plan = medios["TPH"]
    axes[0].bar(["Real","Plan"], [real, plan], color=[PAL[0], "lightgrey"])
    axes[0].set_title("Δ Promedio vs Plan — TPH"); axes[0].yaxis.set_major_formatter(FuncFormatter(sin_dec))
    # Horas
    real, plan = medios["Horas"]
    axes[1].bar(["Real","Plan"], [real, plan], color=[PAL[2], "lightgrey"])
    axes[1].set_title("Δ Promedio vs Plan — Horas"); axes[1].yaxis.set_major_formatter(FuncFormatter(sin_dec))
    for ax in axes: ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return fig

def bullet_vertical(df: pd.DataFrame):
    # gráfico de bala vertical: barras reales por día y línea plan
    fig, axes = plt.subplots(1,2, figsize=(16,6), sharex=True)
    # TPH (usamos real vs plan como línea)
    axes[0].bar(df["Fecha"], df["rendimiento_real_tph"], color=PAL[0], width=0.8)
    axes[0].axhline(df["rendimiento_plan_tph"].median(), color="grey", linestyle="--", label="Plan (mediana)")
    axes[0].set_title("Bala vertical — TPH"); axes[0].set_ylabel("TPH"); axes[0].legend(loc="upper left")
    # Horas
    axes[1].bar(df["Fecha"], df["tiempo_operativo_real_h/dia"], color=PAL[2], width=0.8)
    axes[1].axhline(df["tiempo_operativo_plan_h/dia"].median(), color="grey", linestyle="--", label="Plan (mediana)")
    axes[1].set_title("Bala vertical — Horas/día"); axes[1].set_ylabel("Horas/día"); axes[1].legend(loc="upper left")
    for ax in axes:
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter("%b-%y"))
        ax.yaxis.set_major_formatter(FuncFormatter(sin_dec))
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig

def scatter_tph_horas(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7,6))
    sns.scatterplot(data=df, x="tiempo_operativo_real_h/dia", y="rendimiento_real_tph", s=45, ax=ax, edgecolor="white")
    ax.set_xlabel("Horas/día"); ax.set_ylabel("TPH"); ax.yaxis.set_major_formatter(FuncFormatter(sin_dec))
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig

def percentiles_table(df: pd.DataFrame):
    qs = [0.05,0.25,0.5,0.75,0.95]
    metrics = {
        "TPH real": df["rendimiento_real_tph"].quantile(qs).values,
        "Horas reales": df["tiempo_operativo_real_h/dia"].quantile(qs).values
    }
    out = pd.DataFrame(metrics, index=[f"P{int(q*100)}" for q in qs])
    return out

def anova_por_mes(df: pd.DataFrame):
    res = {}
    try:
        mod1 = smf.ols("rendimiento_real_tph ~ C(mes)", data=df).fit()
        a1 = sm.stats.anova_lm(mod1, typ=2)
        res["TPH por mes"] = a1
    except Exception as e:
        res["TPH por mes"] = pd.DataFrame({"error":[str(e)]})
    try:
        mod2 = smf.ols("tiempo_operativo_real_h/dia ~ C(mes)", data=df).fit()
        a2 = sm.stats.anova_lm(mod2, typ=2)
        res["Horas por mes"] = a2
    except Exception as e:
        res["Horas por mes"] = pd.DataFrame({"error":[str(e)]})
    return res

def heatmap_sensibilidad(df: pd.DataFrame, pct_range=(-10,20,2), dh_range=(-2.0,4.0,0.5)):
    pct = np.arange(pct_range[0], pct_range[1]+1e-9, pct_range[2])
    dh = np.arange(dh_range[0], dh_range[1]+1e-9, dh_range[2])
    base = (df["rendimiento_real_tph"]*df["tiempo_operativo_real_h/dia"]).sum()
    gain = np.zeros((len(dh), len(pct)))
    for i, d in enumerate(dh):
        for j, p in enumerate(pct):
            out = ((df["rendimiento_real_tph"]*(1+p/100.0))*(df["tiempo_operativo_real_h/dia"]+d)).sum()
            gain[i,j] = out - base
    fig, ax = plt.subplots(figsize=(10,6))
    sns.heatmap(gain, cmap="crest", ax=ax,
                xticklabels=[f"{x}%" for x in pct],
                yticklabels=[f"{y:+.1f}h" for y in dh])
    ax.set_title("Ganancia total (t) vs base — grid ΔTPH (%) × Δhoras (h/día)")
    ax.set_xlabel("Δ TPH (%)"); ax.set_ylabel("Δ horas (h/día)")
    fig.tight_layout()
    return fig
