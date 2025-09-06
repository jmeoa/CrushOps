# app.py — hardened
import streamlit as st
import pandas as pd
from io import StringIO
import seaborn as sns
import matplotlib.pyplot as plt

import utils

st.set_page_config(page_title="QuickCrush — Quick Wins Chancado", layout="wide", page_icon="⚡")

st.title("⚡ QuickCrush — Quick Wins en Chancado")
st.caption("App robusta: normaliza columnas y números con coma, antes de KPIs y gráficos.")

with st.sidebar:
    st.header("Carga de datos")
    up = st.file_uploader("Sube tu CSV", type=["csv"])
    st.download_button(
        "Descargar plantilla CSV",
        utils.get_template_csv().encode("utf-8"),
        file_name="plantilla_quickcrush.csv",
        mime="text/csv"
    )

if not up:
    st.info("Sube un CSV para continuar.")
    st.stop()

# Siempre pasar por normalización robusta
try:
    df_std, info = utils.load_dataset(up)
except Exception as e:
    st.error(f"Error al leer/normalizar CSV: {e}")
    st.stop()

st.success("CSV cargado y normalizado correctamente.")
with st.expander("Diagnóstico del dataset"):
    st.json(info, expanded=False)

# KPIs (sobre dataframe ya normalizado)
st.subheader("📊 KPIs")
kpi = utils.calcular_kpis(df_std)  # ya numeric-safe
st.dataframe(kpi.style.format({"Valor": "{:,.2f}"}))

# Gráficos
st.subheader("📈 Gráficos (TPH y Horas)")
fig = utils.graficos_quickcrush(df_std)
st.pyplot(fig, use_container_width=True)
