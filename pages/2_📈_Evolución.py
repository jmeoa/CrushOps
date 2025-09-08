
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.title("📈 Evolución de Parámetros")
df = st.session_state.get("df")

if df is not None:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=df, x="Fecha", y="mineral_procesado_real_t", ax=ax, label="Real")
    sns.lineplot(data=df, x="Fecha", y="mineral_procesado_plan_t", ax=ax, label="Plan")
    ax.set_title("Evolución del Mineral Procesado")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)
else:
    st.error("No hay datos disponibles.")
