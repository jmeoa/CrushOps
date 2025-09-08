
import pandas as pd

def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="ignore")
            except Exception:
                pass
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    return df

def calcular_kpis(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Mineral procesado real (t)": [df["mineral_procesado_real_t"].sum()],
        "Mineral procesado plan (t)": [df["mineral_procesado_plan_t"].sum()],
        "Horas reales": [df["tiempo_operativo_real_h_dia"].sum()],
        "Horas plan": [df["tiempo_operativo_plan_h_dia"].sum()],
    })
