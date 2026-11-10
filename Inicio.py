import pandas as pd
import streamlit as st

# ============================================================
#  Configuración de la página
# ============================================================
st.set_page_config(
    page_title="Análisis de Sensores - Mi Ciudad",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.main { padding: 2rem; }
.stAlert { margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# Nombres que se reconocen como columna de tiempo (sin importar mayúsculas)
CANDIDATAS_TIEMPO = ["time", "_time", "timestamp", "fecha", "date", "datetime", "Time"]


# ============================================================
#  Preparación de datos
# ============================================================
def preparar_datos(df):
    """Detecta la columna de tiempo y las columnas numéricas del CSV.

    Devuelve el DataFrame procesado, la lista de variables numéricas
    y el nombre original de la columna de tiempo (o None).
    """
    df = df.copy()

    # 1. Columna de tiempo → índice
    col_tiempo = next(
        (c for c in df.columns if str(c).strip().lower() in [cand.lower() for cand in CANDIDATAS_TIEMPO]),
        None
    )
    if col_tiempo is not None:
        df[col_tiempo] = pd.to_datetime(df[col_tiempo], errors="coerce")
        df = df.dropna(subset=[col_tiempo]).set_index(col_tiempo).sort_index()
        df.index.name = "Time"

    # 2. Columnas de texto que en realidad son números (p. ej. "23,5")
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            convertida = pd.to_numeric(
                df[c].astype(str).str.replace(",", ".", regex=False),
                errors="coerce"
            )
            if convertida.notna().mean() >= 0.9:
                df[c] = convertida

    # 3. Variables numéricas disponibles para el análisis
    numericas = df.select_dtypes(include="number").columns.tolist()
    return df, numericas, col_tiempo


def normalizar(df):
    """Escala cada columna a 0–1 para comparar variables con unidades distintas."""
    rango = (df.max() - df.min()).replace(0, 1)
    return (df - df.min()) / rango


# ============================================================
#  Encabezado y mapa
# ============================================================
st.title("📊 Análisis de datos de Sensores en Mi Ciudad")
st.markdown("""
    Esta aplicación permite analizar datos de sensores
    recolectados en diferentes puntos de la ciudad.
""")

eafit_location = pd.DataFrame({
    "lat": [6.2006],
    "lon": [-75.5783],
    "location": ["Universidad EAFIT"]
})

st.subheader("📍 Ubicación de los Sensores - Universidad EAFIT")
st.map(eafit_location, zoom=15)

# ============================================================
#  Carga automática de hum.csv y temp.csv
# ============================================================
try:
    # Lectura de los archivos locales ubicados en la raíz del proyecto
    df_hum_raw = pd.read_csv("hum.csv")
    df_temp_raw = pd.read_csv("temp.csv")

    df_hum, vars_hum, col_t_hum = preparar_datos(df_hum_raw)
    df_temp, vars_temp, col_t_temp = preparar_datos(df_temp_raw)

    # Combinar ambos dataframes por marca de tiempo (índice) si es posible
    if not df_hum.empty and not df_temp.empty and isinstance(df_hum.index, pd.DatetimeIndex) and isinstance(df_temp.index, pd.DatetimeIndex):
        df1 = pd.merge(df_temp, df_hum, left_index=True, right_index=True, how="outer").sort_index()
    elif not df_temp.empty:
        df1 = df_temp
    else:
        df1 = df_hum

    variables = df1.select_dtypes(include="number").columns.tolist()
    col_tiempo = df1.index.name if isinstance(df1.index, pd.DatetimeIndex) else None

    if not variables:
        st.error("No se encontraron columnas numéricas válidas en `hum.csv` o `temp.csv`.")
        st.stop()

    st.success(
        f"Se han cargado correctamente los archivos **hum.csv** y **temp.csv**. Variables detectadas: "
        + ", ".join(f"`{v}`" for v in variables)
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Visualización", "📊 Estadísticas", "🔍 Filtros", "🌡️ Confort Térmico", "🗺️ Información del Sitio"]
    )

    # ----------------------------------------------------
    #  TAB 1 · Visualización
    # ----------------------------------------------------
    with tab1:
        st.subheader("Visualización de Datos")

        col_a, col_b = st.columns([3, 1])
        with col_a:
            vars_graf = st.multiselect(
                "Variables a graficar",
                variables,
                default=variables if len(variables) <= 4 else variables[:2]
            )
        with col_b:
            chart_type = st.selectbox("Tipo de gráfico", ["Línea", "Área", "Barra"])

        normalizado = st.checkbox(
            "Normalizar escalas (0–1)",
            help="Útil para comparar variables con unidades distintas, "
                 "por ejemplo temperatura (°C) y humedad (%)."
        )

        if not vars_graf:
            st.warning("Seleccione al menos una variable.")
        else:
            datos_graf = df1[vars_graf]
            if normalizado:
                datos_graf = normalizar(datos_graf)

            if chart_type == "Línea":
                st.line_chart(datos_graf)
            elif chart_type == "Área":
                st.area_chart(datos_graf)
            else:
                st.bar_chart(datos_graf)

        if st.checkbox("Mostrar datos crudos"):
            st.dataframe(df1)

    # ----------------------------------------------------
    #  TAB 2 · Estadísticas
    # ----------------------------------------------------
    with tab2:
        st.subheader("Análisis Estadístico")

        st.write("#### Resumen de todas las variables")
        st.dataframe(df1[variables].describe().T.round(2))

        st.write("#### Detalle por variable")
        var_stats = st.selectbox("Variable", variables, key="var_stats")
        serie = df1[var_stats].dropna()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio", f"{serie.mean():.2f}")
        m2.metric("Máximo", f"{serie.max():.2f}")
        m3.metric("Mínimo", f"{serie.min():.2f}")
        m4.metric("Desv. estándar", f"{serie.std():.2f}")

        if len(variables) >= 2:
            st.write("#### Correlación entre variables")
            st.dataframe(df1[variables].corr().round(2))
            st.caption(
                "Valores cercanos a 1 o −1 indican una relación lineal fuerte; "
                "cercanos a 0, poca relación."
            )

    # ----------------------------------------------------
    #  TAB 3 · Filtros
    # ----------------------------------------------------
    with tab3:
        st.subheader("Filtros de Datos")

        var_filtro = st.selectbox("Variable a filtrar", variables, key="var_filtro")
        min_value = float(df1[var_filtro].min())
        max_value = float(df1[var_filtro].max())

        if min_value == max_value:
            st.warning(f"⚠️ Todos los valores de `{var_filtro}` son iguales: {min_value:.2f}")
            st.info("No es posible aplicar filtros cuando no hay variación en los datos.")
            st.dataframe(df1)
        else:
            rango = st.slider(
                f"Rango de {var_filtro}",
                min_value,
                max_value,
                (min_value, max_value),
                key=f"rango_{var_filtro}"
            )

            filtrado = df1[df1[var_filtro].between(rango[0], rango[1])]
            st.write(
                f"**{len(filtrado)}** de {len(df1)} registros con `{var_filtro}` "
                f"entre {rango[0]:.2f} y {rango[1]:.2f}:"
            )
            st.dataframe(filtrado)

            st.download_button(
                label="⬇️ Descargar datos filtrados (CSV)",
                data=filtrado.to_csv().encode("utf-8"),
                file_name=f"datos_filtrados_{var_filtro}.csv",
                mime="text/csv",
            )

    # ----------------------------------------------------
    #  TAB 4 · Confort Térmico (Definitivo)
    # ----------------------------------------------------
    with tab4:
        st.subheader("🌡️ Análisis de Confort Térmico Ambiental")
        st.markdown("Evaluación automática del nivel de confort basada en las lecturas cruzadas de temperatura y humedad.")

        df_confort = df1.copy()
        
        # Identificamos las columnas numéricas disponibles en el dataframe combinado
        cols_num = df_confort.select_dtypes(include="number").columns.tolist()
        
        # Buscamos la columna de temperatura y de humedad de forma exacta entre las numéricas
        col_temp = next((c for c in cols_num if "temp" in c.lower()), None)
        col_hum = next((c for c in cols_num if "hum" in c.lower()), None)

        # Si por algo no las encuentra por el nombre, tomamos las primeras dos numéricas disponibles
        if not col_temp and len(cols_num) > 0:
            col_temp = cols_num[0]
        if not col_hum and len(cols_num) > 1:
            col_hum = cols_num[1]

        def evaluar_confort(row):
            if not col_temp or not col_hum:
                return "Sin datos"
            
            temp = pd.to_numeric(row[col_temp], errors="coerce")
            hum = pd.to_numeric(row[col_hum], errors="coerce")
            
            if pd.isna(temp) or pd.isna(hum):
                return "Sin datos"
            
            if 20 <= temp <= 26 and 30 <= hum <= 60:
                return "Confortable 🟢"
            elif temp > 26:
                return "Caluroso / Seco 🔴" if hum < 40 else "Caluroso / Húmedo 🟠"
            else:
                return "Frío / Fresco 🔵"

        df_confort["Estado_Confort"] = df_confort.apply(evaluar_confort, axis=1)
        conteo_confort = df_confort["Estado_Confort"].value_counts()

        cc1, cc2 = st.columns([1, 2])
        with cc1:
            st.write("**Distribución de Estados:**")
            st.dataframe(conteo_confort)

        with cc2:
            st.write("**Últimos registros evaluados:**")
            cols_a_mostrar = [c for c in [col_temp, col_hum] if c is not None]
            st.dataframe(df_confort[cols_a_mostrar + ["Estado_Confort"]].tail(5))
            # ----------------------------------------------------
    #  TAB 5 · Información del sitio
    # ----------------------------------------------------
    with tab5:
        st.subheader("Información del Sitio de Medición")

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Ubicación del Sensor")
            st.write("**Universidad EAFIT**")
            st.write("- Latitud: 6.2006")
            st.write("- Longitud: -75.5783")
            st.write("- Altitud: ~1,495 metros sobre el nivel del mar")

        with col2:
            st.write("### Detalles del Sensor")
            st.write("- Tipo: ESP32")
            st.write("- Variables medidas: " + ", ".join(variables))
            st.write(f"- Número de registros: {len(df1)}")
            if col_tiempo is not None and len(df1) > 0:
                st.write(f"- Desde: {df1.index.min():%Y-%m-%d %H:%M}")
                st.write(f"- Hasta: {df1.index.max():%Y-%m-%d %H:%M}")
            st.write("- Ubicación: Campus universitario")

except FileNotFoundError as fnf_err:
    st.error("No se encontraron los archivos `hum.csv` y/o `temp.csv` en el directorio principal.")
    st.info("Por favor, sube `hum.csv` y `temp.csv` a la misma carpeta raíz de tu repositorio en GitHub donde se encuentra `Inicio.py`.")
except Exception as e:
    st.error(f"Error al procesar los archivos locales: {str(e)}")

# ============================================================
#  Pie de página
# ============================================================
st.markdown("""
    ---
    Desarrollado para el análisis de datos de sensores urbanos.
    Ubicación: Universidad EAFIT, Medellín, Colombia
""")
