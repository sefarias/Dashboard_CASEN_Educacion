import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==============================
# CONFIGURACIÓN INICIAL
# ==============================
st.set_page_config(page_title="Dashboard CASEN – Trabajo", layout="wide")

# Ruta del archivo Excel
ruta_excel = r"F:\Users\sfarias\Documents\Curso Python\.vscode\Dashboards-CASEN\Datos\Trabajo\Resultados_Casen_Trabajo.xlsx"

# Cargar todas las hojas del archivo
@st.cache_data
def cargar_datos(ruta):
    xl = pd.ExcelFile(ruta)
    hojas = {}
    for hoja in xl.sheet_names:
        df = xl.parse(hoja, header=None)
        titulo = df.iloc[1, 0] if not pd.isna(df.iloc[1, 0]) else hoja
        hojas[hoja] = {"titulo": titulo, "data": df}
    return hojas

hojas = cargar_datos(ruta_excel)

# ==============================
# INTERFAZ DE USUARIO
# ==============================
st.title("📊 Dashboard CASEN – Trabajo")
st.markdown("Análisis de indicadores laborales a partir de los datos de la **Encuesta CASEN**.")

# Seleccionar hoja (indicador)
nombre_hoja = st.sidebar.selectbox("Selecciona un indicador", list(hojas.keys()))
data_hoja = hojas[nombre_hoja]["data"]
titulo_indicador = hojas[nombre_hoja]["titulo"]

st.subheader(f"Indicador: {titulo_indicador}")

# ==============================
# PROCESAMIENTO DE DATOS
# ==============================

# Buscar las secciones (Estimación, Población expandida, etc.)
secciones = {}
indices = data_hoja.index[data_hoja.iloc[:, 0].astype(str).str.contains("Estimación|Población|Error|Casos", na=False)].tolist()

for i, idx in enumerate(indices):
    nombre = data_hoja.iloc[idx, 0]
    inicio = idx + 1
    fin = indices[i + 1] if i + 1 < len(indices) else len(data_hoja)
    secciones[nombre] = data_hoja.iloc[inicio:fin].dropna(how="all")

# Seleccionar sección a visualizar
nombre_seccion = st.sidebar.selectbox("Selecciona una sección", list(secciones.keys()))
df = secciones[nombre_seccion].copy()

# Limpiar y estructurar los datos
df.columns = df.iloc[0]
df = df[1:]
df = df.rename(columns={df.columns[0]: "Desagregación"})
df = df.melt(id_vars="Desagregación", var_name="Año", value_name="Valor")

# Convertir valores a numéricos
df["Año"] = df["Año"].astype(str)
df["Valor"] = df["Valor"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

# ==============================
# VISUALIZACIONES
# ==============================
col1, col2 = st.columns(2)

with col1:
    fig_line = px.line(
        df,
        x="Año",
        y="Valor",
        color="Desagregación",
        markers=True,
        title=f"Evolución temporal – {nombre_seccion}",
        template="plotly_white"
    )
    fig_line.update_layout(title_x=0.1)
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    fig_bar = px.bar(
        df,
        x="Año",
        y="Valor",
        color="Desagregación",
        barmode="group",
        title=f"Comparación por año – {nombre_seccion}",
        template="plotly_white"
    )
    fig_bar.update_layout(title_x=0.1)
    st.plotly_chart(fig_bar, use_container_width=True)

# ==============================
# TABLA DE DATOS
# ==============================
with st.expander("📄 Ver tabla de datos"):
    st.dataframe(df, use_container_width=True)

st.markdown("---")
st.markdown("**Fuente:** Encuesta CASEN – Ministerio de Desarrollo Social y Familia.")
