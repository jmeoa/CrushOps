import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def calcular_kpis(df):
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    resumen = {
        "Mineral procesado real (t)": df["mineral_procesado_real_t"].sum(),
        "Mineral planificado (t)": df["mineral_procesado_plan_t"].sum(),
        "TPH real promedio": df["rendimiento_real_tph"].mean(),
        "TPH plan promedio": df["rendimiento_plan_tph"].mean(),
        "Horas reales promedio": df["tiempo_operativo_real_h/dia"].mean(),
        "Horas plan promedio": df["tiempo_operativo_plan_h/dia"].mean()
    }
    return pd.DataFrame.from_dict(resumen, orient="index", columns=["Valor"])

def graficos_quickcrush(df):
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Gráfico TPH
    sns.lineplot(data=df, x="Fecha", y="rendimiento_real_tph",
                 ax=axes[0], label="TPH Real", color="#328BA1")
    sns.lineplot(data=df, x="Fecha", y="rendimiento_plan_tph",
                 ax=axes[0], label="TPH Plan", color="grey", linestyle="--")
    axes[0].set_title("Evolución TPH")
    axes[0].tick_params(axis="x", rotation=45)

    # Gráfico Horas
    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_real_h/dia",
                 ax=axes[1], label="Horas Reales", color="#00AFAA")
    sns.lineplot(data=df, x="Fecha", y="tiempo_operativo_plan_h/dia",
                 ax=axes[1], label="Horas Plan", color="grey", linestyle="--")
    axes[1].set_title("Disponibilidad Horas")
    axes[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    return fig
