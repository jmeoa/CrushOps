import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="QuickCrush — Quick Wins Chancado",
                   layout="wide", page_icon="⚡")

st.title("⚡ QuickCrush — Quick Wins en Chancado")
st.caption("EDA robusto con normalización de columnas y números con coma.")

with st.sidebar:
    st.header("Datos")
    up = st.file_uploader("Sube tu CSV", type=["csv"])
    st.download_button("Descargar plantilla CSV",
                       utils.get_template_csv().encode("utf-8"),
                       file_name="plantilla_quickcrush.csv",
                       mime="text/csv")
    st.markdown("---")
    st.caption("Formato esperado: columnas Fecha, TPH, horas y plan (ver plantilla).")

if up is None:
    st.info("Sube un CSV para comenzar y luego navega por las páginas a la izquierda.")
    st.stop()

# Carga robusta y guarda en sesión para las otras páginas
try:
    df, info = utils.load_dataset(up)
except Exception as e:
    st.error(f"Error al leer/normalizar el CSV: {e}")
    st.stop()

st.session_state["quickcrush_df"] = df
st.session_state["quickcrush_info"] = info

st.success("CSV cargado y normalizado. Usa el menú de páginas (izquierda) para ver el análisis.")
with st.expander("Diagnóstico del dataset"):
    st.json(info, expanded=False)

st.dataframe(df.head(20), use_container_width=True)
