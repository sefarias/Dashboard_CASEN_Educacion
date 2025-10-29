import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# CONFIGURACIÓN INICIAL
# ==============================
st.set_page_config(page_title="Dashboard CASEN – Trabajo", layout="wide")

# Ruta del archivo Excel
ruta_excel = r"F:\Users\sfarias\Documents\Curso Python\.vscode\Dashboards-CASEN\Datos\Trabajo\Resultados_Casen_Trabajo.xlsx"

# ==============================
# CARGAR DATOS
# ==============================
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
# FUNCIONES DE PROCESAMIENTO
# ==============================
def procesar_secciones(df_hoja):
    secciones = {}
    n_filas = df_hoja.shape[0]

    for idx, valor in enumerate(df_hoja.iloc[:,0]):
        if pd.isna(valor):
            continue
        nombre_seccion = str(valor).strip()
        if nombre_seccion == "":
            continue

        # Buscar primera fila de datos después del nombre de la sección
        inicio = idx + 1
        while inicio < n_filas and pd.isna(df_hoja.iloc[inicio,1]):
            inicio += 1  # saltar filas vacías hasta la fila que contiene años

        if inicio >= n_filas:
            continue

        # La fila actual es la de encabezados
        df_seccion = df_hoja.iloc[inicio-1: , :].copy()  # incluir fila de encabezado
        df_seccion.columns = df_seccion.iloc[0,:].astype(str)
        df_seccion = df_seccion.iloc[1: , :]

        if df_seccion.shape[0] < 1:
            continue

        df_seccion["Desagregación"] = df_seccion.iloc[:,0].astype(str).str.strip()
        df_seccion = df_seccion.drop(df_seccion.columns[0], axis=1)

        df_seccion = df_seccion.melt(
            id_vars="Desagregación", var_name="Año", value_name="Valor"
        )
        df_seccion["Valor"] = df_seccion["Valor"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df_seccion["Valor"] = pd.to_numeric(df_seccion["Valor"], errors="coerce")
        df_seccion["Año"] = df_seccion["Año"].astype(str)

        secciones[nombre_seccion] = df_seccion

    return secciones


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

# Procesar secciones de la hoja seleccionada
secciones = procesar_secciones(data_hoja)

# Manejo seguro si no hay secciones detectadas
if len(secciones) == 0:
    st.warning("❌ No se detectaron secciones en esta hoja. Revisa el Excel.")
else:
    # Seleccionar sección
    nombre_seccion = st.sidebar.selectbox("Selecciona sección", list(secciones.keys()))
    df = secciones[nombre_seccion]

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
