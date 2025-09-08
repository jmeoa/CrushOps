
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import streamlit as st

custom_palette = ["#328BA1", "#00AFAA", "#145374", "#5588A3"]

def _numeric_guard(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_dataset(file):
    df = pd.read_csv(file)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
    df = _numeric_guard(df)
    return df

def calcular_kpis(df):
    df = _numeric_guard(df)
    kpis = {
        "Mineral procesado real (t)": df.get("mineral_procesado_real_t", pd.Series(dtype=float)).sum(skipna=True),
        "Mineral procesado plan (t)": df.get("mineral_procesado_plan_t", pd.Series(dtype=float)).sum(skipna=True),
        "TPH promedio real": df.get("rendimiento_real_tph", pd.Series(dtype=float)).mean(skipna=True),
        "TPH promedio plan": df.get("rendimiento_plan_tph", pd.Series(dtype=float)).mean(skipna=True),
        "Horas operativas promedio": df.get("tiempo_operativo_real_h/dia", pd.Series(dtype=float)).mean(skipna=True)
    }
    return pd.DataFrame(kpis, index=[0])

def graficos_quickcrush(df):
    df = _numeric_guard(df)
    df = df.sort_values("fecha")

    fig, axes = plt.subplots(2, 2, figsize=(16, 9))

    sns.lineplot(data=df, x="fecha", y="rendimiento_real_tph", ax=axes[0,0],
                 color=custom_palette[0], label="TPH real")
    if "rendimiento_plan_tph" in df.columns:
        axes[0,0].axhline(df["rendimiento_plan_tph"].median(), color="grey", linestyle="--", label="Plan")
    axes[0,0].set_title("Evolución diaria TPH")
    axes[0,0].legend()

    sns.lineplot(data=df, x="fecha", y="tiempo_operativo_real_h/dia", ax=axes[0,1],
                 color=custom_palette[1], label="Horas reales")
    if "tiempo_operativo_plan_h/dia" in df.columns:
        axes[0,1].axhline(df["tiempo_operativo_plan_h/dia"].median(), color="grey", linestyle="--", label="Plan")
    axes[0,1].set_title("Evolución diaria horas")
    axes[0,1].legend()

    if "rendimiento_real_tph" in df.columns and "mes" not in df.columns:
        df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    if "rendimiento_real_tph" in df.columns:
        sns.boxplot(data=df, x="mes", y="rendimiento_real_tph", ax=axes[1,0], palette=custom_palette)
        axes[1,0].set_title("Variabilidad TPH por mes")
        axes[1,0].tick_params(axis="x", rotation=45)

    if "tiempo_operativo_real_h/dia" in df.columns and "rendimiento_real_tph" in df.columns:
        sns.scatterplot(data=df, x="tiempo_operativo_real_h/dia", y="rendimiento_real_tph",
                        ax=axes[1,1], color=custom_palette[2])
        axes[1,1].set_title("Dispersión TPH vs horas")

    plt.tight_layout()
    st.pyplot(fig)

def get_template_csv():
    cols = ["Fecha", "mineral_procesado_real_t", "rendimiento_real_tph", "tiempo_operativo_real_h/dia",
            "mineral_procesado_plan_t", "rendimiento_plan_tph", "tiempo_operativo_plan_h/dia"]
    df = pd.DataFrame(columns=cols)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()
