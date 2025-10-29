import streamlit as st
import pandas as pd
import plotly.express as px
import os

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Dashboard CASEN Educación", layout="wide")

# Ruta del archivo
ruta_excel = r"F:\Users\sfarias\Documents\Curso Python\.vscode\Dashboards-CASEN\Educacion_Dashboard\Educación_Casen_2024.xlsx"

# === CARGA DE HOJAS ===
if not os.path.exists(ruta_excel):
    st.error("No se encontró el archivo Excel en la ruta especificada.")
    st.stop()

xls = pd.ExcelFile(ruta_excel)
hojas = xls.sheet_names

st.sidebar.title("Opciones de navegación")
hoja_seleccionada = st.sidebar.selectbox("Selecciona la hoja", hojas)

df = pd.read_excel(ruta_excel, sheet_name=hoja_seleccionada)

st.title(f"📊 Dashboard Educación CASEN - Hoja {hoja_seleccionada}")

# Mostrar las primeras filas
st.dataframe(df.head())

# === DETECTAR GRUPOS DE COLUMNAS ===
prefijos = ["Est_", "Err_", "n_", "N_"]
grupos = {p: [c for c in df.columns if c.startswith(p)] for p in prefijos}

grupo_seleccionado = st.sidebar.selectbox(
    "Selecciona grupo de columnas para graficar",
    list(grupos.keys())
)

cols = grupos.get(grupo_seleccionado, [])
if len(cols) == 0:
    st.warning("No se encontraron columnas para ese grupo.")
    st.stop()

# === TRANSFORMACIÓN ===
df_melt = df.melt(
    id_vars=["Categoría", "Nivel", "D1"],
    value_vars=cols,
    var_name="Año",
    value_name="Valor"
)

# Limpiar nombres de año (Est_2006 → 2006)
df_melt["Año"] = df_melt["Año"].str.extract(r"(\d+)").astype(int)

# === FILTROS ===
categoria_sel = st.sidebar.selectbox(
    "Selecciona una categoría",
    df_melt["Categoría"].unique()
)

nivel_sel = st.sidebar.selectbox(
    "Selecciona un nivel",
    df_melt["Nivel"].unique()
)

df_filtrado = df_melt[
    (df_melt["Categoría"] == categoria_sel) &
    (df_melt["Nivel"] == nivel_sel)
]

# === GRÁFICO INTERACTIVO ===
st.subheader(f"{grupo_seleccionado} para {categoria_sel} - Nivel {nivel_sel}")

fig = px.line(
    df_filtrado,
    x="Año",
    y="Valor",
    markers=True,
    title=f"Evolución de {grupo_seleccionado} ({categoria_sel}, {nivel_sel})"
)
fig.update_layout(title_x=0.5, template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# === TABLA DETALLADA ===
st.subheader("Tabla de datos filtrados")
st.dataframe(df_filtrado)
