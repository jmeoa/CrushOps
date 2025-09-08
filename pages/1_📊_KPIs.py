
import streamlit as st
import utils

st.title("📊 KPIs de Producción")
df = st.session_state.get("df")

if df is not None:
    kpi_df = utils.calcular_kpis(df)
    st.dataframe(kpi_df)
else:
    st.error("No hay datos disponibles.")
