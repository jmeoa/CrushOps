# app.py (robust/fixed)
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO

import utils  # debe existir en el repo

st.set_page_config(page_title="QuickCrush - Quick Wins en Chancado",
                   layout="wide",
                   page_icon="⚡")

st.title("⚡ QuickCrush — Quick Wins en Chancado")
st.caption("EDA profesional con métricas, gráficos y quick wins operacionales.")

# --- Fallback local si utils no tiene get_template_csv ---
def _local_template_csv() -> str:
    return (
        "Fecha,mineral_procesado_real_t,rendimiento_real_tph,tiempo_operativo_real_h/dia,"
        "mineral_procesado_plan_t,rendimiento_plan_tph,tiempo_operativo_plan_h/dia\n"
        "2025-01-01,40,2,20,41,2.1,19.5\n"
        "2025-01-02,38,1.9,20,41,2.1,19.5\n"
    )

def get_template_csv_safe() -> str:
    return getattr(utils, "get_template_csv", _local_template_csv)()

with st.sidebar:
    st.header("Carga de datos")
    uploaded_file = st.file_uploader("Sube tu dataset CSV", type=["csv"])
    st.markdown("¿Sin archivo? Descarga la **plantilla**:")
    st.download_button(
        label="Descargar plantilla CSV",
        data=get_template_csv_safe().encode("utf-8"),
        file_name="plantilla_quickcrush.csv",
        mime="text/csv"
    )

if not uploaded_file:
    st.info("Sube tu CSV para comenzar. La app normaliza columnas y números con comas (p. ej., 2,100).")
    st.stop()

# --- Carga robusta del CSV: usa utils.load_dataset si existe, si no, lectura mínima ---
def load_dataset_safe(file):
    if hasattr(utils, "load_dataset"):
        return utils.load_dataset(file)
    # fallback simple (sin normalización avanzada)
    raw = file.read().decode("utf-8", errors="ignore")
    try:
        df = pd.read_csv(StringIO(raw))
    except Exception:
        df = pd.read_csv(StringIO(raw), sep=";")
    info = {"mapeo_columnas": "fallback_simple", "filas": len(df)}
    return df, info

try:
    df, info = load_dataset_safe(uploaded_file)
except Exception as e:
    st.error(f"Error al leer/normalizar el CSV: {e}")
    st.stop()

st.success("CSV cargado correctamente.")
with st.expander("Ver diagnóstico de columnas mapeadas/lectura"):
    st.json(info, expanded=False)

# --- KPIs ---
st.subheader("📊 KPIs principales")
if hasattr(utils, "calcular_kpis"):
    kpi_df = utils.calcular_kpis(df)
else:
    st.warning("utils.calcular_kpis no encontrado: mostrando primeras filas del dataset.")
    kpi_df = df.head()
st.dataframe(kpi_df)

# --- Gráficos ---
st.subheader("📈 Gráficos")
if hasattr(utils, "graficos_quickcrush"):
    fig = utils.graficos_quickcrush(df)
    st.pyplot(fig, use_container_width=True)
else:
    st.warning("utils.graficos_quickcrush no encontrado: grafico rápido de TPH real vs fecha.")
    if "Fecha" in df.columns and "rendimiento_real_tph" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df.dropna(subset=["Fecha"])
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.lineplot(data=df, x="Fecha", y="rendimiento_real_tph", ax=ax, color="#328BA1")
        ax.set_title("Evolución TPH (rápido)")
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No encuentro columnas 'Fecha' y/o 'rendimiento_real_tph' para el gráfico de respaldo.")
