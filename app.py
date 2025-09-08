
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import utils

st.set_page_config(page_title="QuickCrush — Chancado Quick Wins", layout="wide", page_icon="⚡")

st.title("⚡ QuickCrush — Chancado Quick Wins")
st.caption("EDA robusto con normalización de columnas y números con comas.")

with st.sidebar:
    st.header("Datos")
    up = st.file_uploader("Sube tu CSV", type=["csv"])
    st.download_button(
        "Descargar plantilla CSV",
        utils.get_template_csv().encode("utf-8"),
        file_name="plantilla_quickcrush.csv",
        mime="text/csv"
    )

if up is None:
    st.info("Sube un CSV para comenzar.")
    st.stop()

# Carga robusta
try:
    df, info = utils.load_dataset(up)
except Exception as e:
    st.error(f"Error al leer/normalizar el CSV: {e}")
    st.stop()

st.success("CSV cargado y normalizado.")
with st.expander("Diagnóstico del dataset"):
    st.json(info, expanded=False)

# KPIs
st.subheader("📊 KPIs")
kpi = utils.calcular_kpis(df)
st.dataframe(kpi.style.format({'Valor': '{:,.2f}'}), use_container_width=True)

# Gráficos
st.subheader("📈 Gráficos")
fig = utils.graficos_quickcrush(df)
st.pyplot(fig, use_container_width=True)
