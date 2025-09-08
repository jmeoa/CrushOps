
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter, MonthLocator
import statsmodels.api as sm
from statsmodels.formula.api import ols

# ===== Config general =====
st.set_page_config(page_title="QuickCrush — Consolidado", layout="wide", page_icon="⚡")
PALETTE = ["#328BA1", "#0B5563", "#00AFAA", "#66C7C7", "#BFD8D2"]
sns.set_theme(style="whitegrid", palette=PALETTE)

# ===== Utilidades =====
def fmt_int(x, pos=None):
    try: return f"{int(round(x)):,}".replace(",", ".")
    except: return ""

def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(
        s.astype(str)
         .str.replace(".", "", regex=False)  # elimina separador de miles estilo es-CL
         .str.replace(",", "", regex=False)  # elimina coma si viene como miles
         .str.replace(" ", "", regex=False)
         .str.replace("\u00a0","", regex=False)
         .str.strip(),
        errors="coerce"
    )

@st.cache_data
def load_data(file) -> pd.DataFrame:
    if file is None:
        df = pd.read_csv("dataset_chancado.csv")
    else:
        df = pd.read_csv(file)
    # normalización de nombres mínimos esperados
    cols = {c.lower().replace("/", "_").replace(" ", "_"): c for c in df.columns}
    expected = {
        "fecha":"Fecha",
        "mineral_procesado_real_t":"mineral_procesado_real_t",
        "rendimiento_real_tph":"rendimiento_real_tph",
        "tiempo_operativo_real_h_dia":"tiempo_operativo_real_h/dia",
        "mineral_procesado_plan_t":"mineral_procesado_plan_t",
        "rendimiento_plan_tph":"rendimiento_plan_tph",
        "tiempo_operativo_plan_h_dia":"tiempo_operativo_plan_h/dia",
    }
    # mapear si hay alias
    mapping = {}
    for k,std in expected.items():
        mapping[std] = df.columns[[c for c in cols if k==c].index(0)] if k in cols else std if std in df.columns else None
    # construir salida
    out = pd.DataFrame()
    # fecha
    fcol = mapping["Fecha"] if "Fecha" in mapping and mapping["Fecha"] is not None else ("Fecha" if "Fecha" in df.columns else list(df.columns)[0])
    out["Fecha"] = pd.to_datetime(df[fcol], errors="coerce", dayfirst=True)
    # numéricas
    for std in [c for c in expected.values() if c!="Fecha"]:
        src = mapping.get(std, std)
        if src not in df.columns:
            raise ValueError(f"Falta columna requerida: {std}")
        out[std] = to_num(df[src])
    out = out.dropna(subset=["Fecha"]).sort_values("Fecha").reset_index(drop=True)
    out["mes"] = out["Fecha"].dt.to_period("M").astype(str)
    return out

def kpis(df: pd.DataFrame) -> pd.DataFrame:
    d = {
        "Mineral real (t)": df["mineral_procesado_real_t"].sum(),
        "Mineral plan (t)": df["mineral_procesado_plan_t"].sum(),
        "Δ Mineral (t)": df["mineral_procesado_real_t"].sum() - df["mineral_procesado_plan_t"].sum(),
        "TPH real promedio": df["rendimiento_real_tph"].mean(),
        "TPH plan promedio": df["rendimiento_plan_tph"].mean(),
        "Horas reales promedio": df["tiempo_operativo_real_h/dia"].mean(),
        "Horas plan promedio": df["tiempo_operativo_plan_h/dia"].mean(),
    }
    return pd.DataFrame.from_dict(d, orient="index", columns=["Valor"])

# ===== Gráficos =====
def bullet_vertical(df: pd.DataFrame):
    fig, axes = plt.subplots(1,2, figsize=(16,6), sharex=False)
    # TPH
    axes[0].bar(df["Fecha"], df["rendimiento_real_tph"], color=PALETTE[0])
    axes[0].axhline(df["rendimiento_plan_tph"].median(), color="grey", linestyle="--", label="Plan (mediana)")
    axes[0].set_title("Bala vertical — TPH"); axes[0].set_ylabel("TPH"); axes[0].legend(loc="upper left")
    # Horas
    axes[1].bar(df["Fecha"], df["tiempo_operativo_real_h/dia"], color=PALETTE[2])
    axes[1].axhline(df["tiempo_operativo_plan_h/dia"].median(), color="grey", linestyle="--", label="Plan (mediana)")
    axes[1].set_title("Bala vertical — Horas/día"); axes[1].set_ylabel("Horas/día"); axes[1].legend(loc="upper left")
    for ax in axes:
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter("%b-%y"))
        ax.yaxis.set_major_formatter(FuncFormatter(fmt_int))
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig

def evolucion(df: pd.DataFrame):
    fig, axes = plt.subplots(1,2, figsize=(18,6), sharex=True)
    sns.lineplot(data=df, x="Fecha", y="rendimiento_real_tph", ax=axes[0], label="TPH real", color=PALETTE[0])
    sns.lineplot(data=df, x="Fecha", y="rendimiento_plan_tph", ax=axes[0], label="TPH plan", color="grey", linestyle="--")
    axes[0].set_title("Evolución diaria TPH"); axes[0].yaxis.set_major_formatter(FuncFormatter(fmt_int))
    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_real_h/dia", ax=axes[1], label="Horas reales", color=PALETTE[2])
    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_plan_h/dia", ax=axes[1], label="Horas plan", color="grey", linestyle="--")
    axes[1].set_title("Evolución diaria Horas"); axes[1].yaxis.set_major_formatter(FuncFormatter(fmt_int))
    for ax in axes:
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter("%b-%y"))
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig

def delta_prom(df: pd.DataFrame):
    fig, axes = plt.subplots(1,2, figsize=(14,5))
    # TPH
    axes[0].bar(["Real","Plan"], [df["rendimiento_real_tph"].mean(), df["rendimiento_plan_tph"].mean()],
                color=[PALETTE[0], "lightgrey"])
    axes[0].set_title("Δ Promedio vs plan — TPH"); axes[0].yaxis.set_major_formatter(FuncFormatter(fmt_int))
    # Horas
    axes[1].bar(["Real","Plan"], [df["tiempo_operativo_real_h/dia"].mean(), df["tiempo_operativo_plan_h/dia"].mean()],
                color=[PALETTE[2], "lightgrey"])
    axes[1].set_title("Δ Promedio vs plan — Horas"); axes[1].yaxis.set_major_formatter(FuncFormatter(fmt_int))
    for ax in axes: ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return fig

def scatter(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7,6))
    sns.scatterplot(data=df, x="tiempo_operativo_real_h/dia", y="rendimiento_real_tph", s=45, edgecolor="white", ax=ax, color=PALETTE[0])
    ax.set_xlabel("Horas/día"); ax.set_ylabel("TPH")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_int))
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig

def percentiles(df: pd.DataFrame):
    qs = [0.05,0.25,0.5,0.75,0.95]
    tb = pd.DataFrame({
        "TPH real": df["rendimiento_real_tph"].quantile(qs).values,
        "Horas reales": df["tiempo_operativo_real_h/dia"].quantile(qs).values
    }, index=[f"P{int(q*100)}" for q in qs])
    return tb

def anova(df: pd.DataFrame):
    res = {}
    try:
        mod = ols("rendimiento_real_tph ~ C(mes)", data=df).fit()
        res["TPH por mes"] = sm.stats.anova_lm(mod, typ=2)
    except Exception as e:
        res["TPH por mes"] = pd.DataFrame({"error":[str(e)]})
    try:
        mod2 = ols("tiempo_operativo_real_h/dia ~ C(mes)", data=df).fit()
        res["Horas por mes"] = sm.stats.anova_lm(mod2, typ=2)
    except Exception as e:
        res["Horas por mes"] = pd.DataFrame({"error":[str(e)]})
    return res

def heatmap_sensibilidad(df: pd.DataFrame, pct_range=(-10, 20, 2), dh_range=(-2.0, 4.0, 0.5)):
    pct = np.arange(pct_range[0], pct_range[1]+1e-9, pct_range[2])
    dh  = np.arange(dh_range[0],  dh_range[1]+1e-9,  dh_range[2])
    base = (df["rendimiento_real_tph"]*df["tiempo_operativo_real_h/dia"]).sum()
    gain = np.zeros((len(dh), len(pct)))
    for i, d in enumerate(dh):
        for j, p in enumerate(pct):
            out = ((df["rendimiento_real_tph"]*(1+p/100.0)) * (df["tiempo_operativo_real_h/dia"]+d)).sum()
            gain[i,j] = out - base
    fig, ax = plt.subplots(figsize=(10,6))
    sns.heatmap(gain, ax=ax, cmap="crest",
                xticklabels=[f"{x}%" for x in pct],
                yticklabels=[f"{y:+.1f}h" for y in dh])
    ax.set_title("Ganancia total (t) vs base — ΔTPH (%) × Δhoras (h/día)")
    ax.set_xlabel("Δ TPH (%)"); ax.set_ylabel("Δ horas (h/día)")
    fig.tight_layout()
    return fig

# ===== UI =====
st.title("⚡ QuickCrush — Análisis Consolidado (Single File)")
with st.sidebar:
    st.header("Datos")
    up = st.file_uploader("Sube CSV", type=["csv"])
    st.caption("Si no subes archivo, se usa dataset_chancado.csv (ejemplo).")

df = load_data(up)

st.success(f"Filas: {len(df):,}  |  Rango: {df['Fecha'].min().date()} → {df['Fecha'].max().date()}")

# KPIs (ligero)
st.subheader("🔑 KPIs")
kpi = kpis(df)
st.dataframe(kpi.style.format({"Valor":"{:,.2f}"}), use_container_width=True)

# Para evitar 'oven', render perezoso por secciones
with st.expander("🎯 Bala vertical — Real vs Plan (TPH y Horas)", expanded=True):
    st.pyplot(bullet_vertical(df), use_container_width=True)

with st.expander("📈 Evolución temporal (TPH / Horas)", expanded=False):
    st.pyplot(evolucion(df), use_container_width=True)

with st.expander("Δ Promedio vs plan (TPH y Horas)", expanded=False):
    st.pyplot(delta_prom(df), use_container_width=True)

with st.expander("🔎 Dispersión TPH vs Horas", expanded=False):
    st.pyplot(scatter(df), use_container_width=True)

with st.expander("📐 Percentiles (TPH / Horas)", expanded=False):
    st.dataframe(percentiles(df).style.format("{:,.2f}"), use_container_width=True)

with st.expander("🧪 ANOVA por mes (TPH / Horas)", expanded=False):
    a = anova(df)
    c1, c2 = st.columns(2)
    with c1: st.caption("TPH por mes"); st.dataframe(a["TPH por mes"], use_container_width=True)
    with c2: st.caption("Horas por mes"); st.dataframe(a["Horas por mes"], use_container_width=True)

with st.expander("🛰️ Sensibilidad — ΔTPH vs Δhoras", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        pct_min = st.number_input("ΔTPH min (%)", value=-10)
        pct_max = st.number_input("ΔTPH max (%)", value=20)
        pct_step = st.number_input("Paso ΔTPH (%)", value=2)
    with col2:
        dh_min = st.number_input("Δhoras min (h)", value=-2.0, step=0.1)
        dh_max = st.number_input("Δhoras max (h)", value=4.0, step=0.1)
        dh_step = st.number_input("Paso Δhoras (h)", value=0.5, step=0.1)
    if st.button("Generar heatmap de sensibilidad"):
        st.pyplot(heatmap_sensibilidad(df, (pct_min, pct_max, pct_step), (dh_min, dh_max, dh_step)), use_container_width=True)

st.download_button("⬇️ Descargar datos limpios", df.to_csv(index=False).encode("utf-8"),
                   file_name="datos_limpios_quickcrush.csv", mime="text/csv")
