import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import utils

st.set_page_config(page_title="QuickCrush - Quick Wins en Chancado",
                   layout="wide",
                   page_icon="🔍")

st.title("🔍 QuickCrush — Quick Wins en Chancado")
st.markdown("De los datos a victorias rápidas en rendimiento y disponibilidad.")

uploaded_file = st.file_uploader("Sube tu dataset CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Datos cargados correctamente.")

    # --- KPIs ---
    st.subheader("📊 KPIs principales")
    kpi_df = utils.calcular_kpis(df)
    st.dataframe(kpi_df)

    # --- Gráficos ---
    st.subheader("📈 Gráficos")
    fig = utils.graficos_quickcrush(df)
    st.pyplot(fig)
