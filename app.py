
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import utils

st.set_page_config(page_title="QuickCrush — Análisis Consolidado", layout="wide", page_icon="⚡")
st.title("⚡ QuickCrush — Análisis Consolidado (Single Page)")

st.caption("Sube tu CSV o usa el dataset de ejemplo para ver todo el análisis en una sola vista.")

up = st.file_uploader("CSV con columnas: Fecha, TPH/horas real & plan", type=["csv"])

if up is None:
    st.warning("No se subió archivo. Usando dataset de ejemplo incluido.")
    df = utils.load_dataset("dataset_chancado.csv")
else:
    try:
        df = utils.load_dataset(up)
    except Exception as e:
        st.error(f"Error al cargar/normalizar el CSV: {e}")
        st.stop()

st.success(f"Dataset cargado. Filas: {len(df):,} — rango: {df['Fecha'].min().date()} a {df['Fecha'].max().date()}")

# ======= KPIs =======
st.header("📊 KPIs clave")
kpi = utils.calcular_kpis(df)
st.dataframe(kpi.style.format({"Valor":"{:,.2f}"}), use_container_width=True)

# ======= Gráfico de bala vertical (TPH / Horas) =======
st.header("🎯 Gráficos de bala (vertical) — Real vs Plan (línea mediana plan)")
fig_bullet = utils.bullet_vertical(df)
st.pyplot(fig_bullet, use_container_width=True)

# ======= Evolución temporal =======
st.header("📈 Evolución temporal (TPH / Horas)")
fig_ev = utils.evolucion_tph_horas(df)
st.pyplot(fig_ev, use_container_width=True)

# ======= Δ Promedio vs plan (separado TPH y Horas) =======
st.header("Δ promedio vs plan")
fig_delta = utils.barras_delta_prom(df)
st.pyplot(fig_delta, use_container_width=True)

# ======= Dispersión TPH vs Horas =======
st.header("🔎 Dispersión TPH vs horas (variabilidad conjunta)")
fig_sc = utils.scatter_tph_horas(df)
st.pyplot(fig_sc, use_container_width=True)

# ======= Percentiles =======
st.header("📐 Percentiles (TPH y Horas)")
ptable = utils.percentiles_table(df)
st.dataframe(ptable.style.format("{:,.2f}"), use_container_width=True)

# ======= ANOVA por mes =======
st.header("🧪 ANOVA por mes (TPH y Horas)")
anova = utils.anova_por_mes(df)
col1, col2 = st.columns(2)
with col1:
    st.subheader("TPH por mes")
    st.dataframe(anova["TPH por mes"], use_container_width=True)
with col2:
    st.subheader("Horas por mes")
    st.dataframe(anova["Horas por mes"], use_container_width=True)

# ======= Sensibilidad (heatmap) =======
st.header("🛰️ Sensibilidad: ΔTPH (%) × Δhoras (h/día) → Ganancia total (t)")
fig_hm = utils.heatmap_sensibilidad(df)
st.pyplot(fig_hm, use_container_width=True)

st.caption("Notas: Seaborn + Matplotlib (Agg). Paleta profesional y ejes sin decimales. "
           "Las medianas de plan se usan como referencia en bala vertical.")
