# app.py (robust)
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO

import utils

st.set_page_config(page_title="QuickCrush - Quick Wins en Chancado",
                   layout="wide",
                   page_icon="⚡")

st.title("⚡ QuickCrush — Quick Wins en Chancado")
st.caption("EDA profesional con métricas, gráficos y quick wins operacionales.")

with st.sidebar:
    st.header("Carga de datos")
    uploaded_file = st.file_uploader("Sube tu dataset CSV", type=["csv"])
    st.markdown("¿Sin archivo? Descarga la **plantilla**:")
    st.download_button("Descargar plantilla CSV", utils.get_template_csv(), file_name="plantilla_quickcrush.csv", mime="text/csv")

if not uploaded_file:
    st.info("Sube tu CSV para comenzar. La app normaliza columnas y números con comas (ej: 2,100).")
    st.stop()

# --- Carga robusta ---
try:
    df, info = utils.load_dataset(uploaded_file)
except Exception as e:
    st.error(f"Error al leer/normalizar el CSV: {e}")
    st.stop()

st.success("CSV cargado correctamente.")
with st.expander("Ver diagnóstico de columnas mapeadas"):
    st.json(info, expanded=False)

# --- KPIs ---
st.subheader("📊 KPIs principales")
kpi_df = utils.calcular_kpis(df)
st.dataframe(kpi_df.style.format({"Valor": "{:,.2f}"}))

# --- Gráficos ---
st.subheader("📈 Gráficos")
fig = utils.graficos_quickcrush(df)
st.pyplot(fig, use_container_width=True)
