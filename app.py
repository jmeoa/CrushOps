
import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="QuickCrush", layout="wide")

st.title("⚡ QuickCrush: Quick Wins en Chancado")
st.markdown("### Bienvenido a la app de análisis y optimización del chancado")

st.info("Usa el menú lateral para navegar entre KPIs, Evolución, Sensibilidad y Variabilidad.")

uploaded_file = st.file_uploader("Sube un archivo CSV con tus datos", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.warning("No se subió archivo, usando dataset de ejemplo.")
    df = pd.read_csv("dataset_chancado.csv")

st.session_state["df"] = utils.limpiar_datos(df)
