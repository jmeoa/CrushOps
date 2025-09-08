
import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="QuickCrush", layout="wide")

st.title("QuickCrush – Chancado Quick Wins Dashboard")

# Subida de archivo
uploaded_file = st.file_uploader("Sube el dataset CSV de chancado", type=["csv"])

if uploaded_file:
    df = utils.load_dataset(uploaded_file)
    st.subheader("Diagnóstico del dataset")
    st.write(df.head())
    st.write(df.dtypes)

    # KPI
    kpi_df = utils.calcular_kpis(df)
    st.subheader("Indicadores Clave (KPI)")
    st.dataframe(kpi_df)

    # Gráficos
    st.subheader("Visualizaciones")
    utils.graficos_quickcrush(df)

# Descargar plantilla
st.download_button("Descargar plantilla CSV", utils.get_template_csv(), file_name="plantilla_quickcrush.csv", mime="text/csv")
