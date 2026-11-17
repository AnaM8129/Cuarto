import pandas as pd
import streamlit as st

# ============================================================
#  Configuración de la página
# ============================================================
st.set_page_config(
    page_title="Análisis de Sensores - EAFIT",
    page_icon="📊",
    layout="wide"
)

# ============================================================
#  Estilos CSS personalizados (Diseño Moderno de Tarjetas y Dashboard)
# ============================================================
st.markdown("""
<style>
    /* Estilo general del fondo y contenedores */
    .main {
        background-color: #F8F9FA;
        padding: 1.5rem;
    }
    
    /* Contenedores tipo tarjeta */
    div.stMarkdown, div.element-container {
        color: #2C3E50;
    }
    
    /* Tarjetas personalizadas para métricas o secciones */
    .dashboard-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #E9ECEF;
    }

    /* Estilización de pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #F1F3F5;
        border-radius: 8px;
        color: #495057;
        font-weight: 600;
        padding: 0 16px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3182CE !important;
        color: white !important;
    }

    /* Botones y descargas */
    .stButton>button, .stDownloadButton>button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
    }
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
#  Encabezado Principal Estilizado
# ============================================================
st.markdown("""
    <div style="padding: 1.5rem 0; border-bottom: 2px solid #E9ECEF; margin-bottom: 2rem;">
        <h1 style="color: #1A365D; font-weight: 800; margin-bottom: 0.2rem;">📊 Panel de Control IoT - Sensores Urbanos</h1>
        <p style="color: #718096; font-size: 1.1rem;">Sistema avanzado de monitoreo ambiental, análisis de confort y telemetría en tiempo real.</p>
    </div>
""", unsafe_allow_html=True)

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
        f"✅ Se han cargado correctamente los archivos **hum.csv** y **temp.csv**. Variables detectadas: "
        + ", ".join(f"`{v}`" for v in variables)
    )

    # Pestañas principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Visualización", "📊 Estadísticas", "🔍 Filtros", "🌡️ Confort Térmico", "🗺️ Información del Sitio"]
    )

    # ----------------------------------------------------
    #  TAB 1 · Visualización
    # ----------------------------------------------------
    with tab1:
        st.markdown("### 📈 Visualización Gráfica de Sensores")
        
        with st.container():
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
                help="Útil para comparar variables con unidades distintas, por ejemplo temperatura (°C) y humedad (%)."
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
                st.dataframe(df1, use_container_width=True)

    # ----------------------------------------------------
    #  TAB 2 · Estadísticas
    # ----------------------------------------------------
    with tab2:
        st.markdown("### 📊 Resumen Estadístico Analítico")

        st.markdown("#### Descriptivas Generales")
        st.dataframe(df1[variables].describe().T.round(2), use_container_width=True)

        st.markdown("#### Detalle por Variable")
        var_stats = st.selectbox("Seleccione variable para métricas", variables, key="var_stats")
        serie = df1[var_stats].dropna()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio", f"{serie.mean():.2f}")
        m2.metric("Máximo", f"{serie.max():.2f}")
        m3.metric("Mínimo", f"{serie.min():.2f}")
        m4.metric("Desv. Estándar", f"{serie.std():.2f}")

        if len(variables) >= 2:
            st.markdown("#### Matriz de Correlación")
            st.dataframe(df1[variables].corr().round(2), use_container_width=True)
            st.caption("Valores cercanos a 1 o −1 indican una relación lineal fuerte; cercanos a 0, poca relación.")

    # ----------------------------------------------------
    #  TAB 3 · Filtros
    # ----------------------------------------------------
    with tab3:
        st.markdown("### 🔍 Filtrado Avanzado de Datos")

        var_filtro = st.selectbox("Variable a filtrar", variables, key="var_filtro")
        min_value = float(df1[var_filtro].min())
        max_value = float(df1[var_filtro].max())

        if min_value == max_value:
            st.warning(f"⚠️ Todos los valores de `{var_filtro}` son iguales: {min_value:.2f}")
            st.info("No es posible aplicar filtros cuando no hay variación en los datos.")
            st.dataframe(df1, use_container_width=True)
        else:
            rango = st.slider(
                f"Rango de {var_filtro}",
                min_value,
                max_value,
                (min_value, max_value),
                key=f"rango_{var_filtro}"
            )

            filtrado = df1[df1[var_filtro].between(rango[0], rango[1])]
            st.markdown(f"**{len(filtrado)}** de {len(df1)} registros con `{var_filtro}` entre **{rango[0]:.2f}** y **{rango[1]:.2f}**:")
            st.dataframe(filtrado, use_container_width=True)

            st.download_button(
                label="⬇️ Descargar datos filtrados (CSV)",
                data=filtrado.to_csv().encode("utf-8"),
                file_name=f"datos_filtrados_{var_filtro}.csv",
                mime="text/csv",
            )

    # ----------------------------------------------------
    #  TAB 4 · Confort Térmico (Lectura Directa)
    # ----------------------------------------------------
    with tab4:
        st.markdown("### 🌡️ Análisis de Confort Térmico Ambiental")
        st.markdown("Evaluación automática del nivel de confort basada en las lecturas directas de temperatura y humedad.")

        # Leemos los dataframes limpios de forma independiente para asegurar los datos
        df_t_local, _, _ = preparar_datos(df_temp_raw)
        df_h_local, _, _ = preparar_datos(df_hum_raw)

        c_t = next((c for c in df_t_local.select_dtypes(include="number").columns if "temp" in c.lower()), None)
        c_h = next((c for c in df_h_local.select_dtypes(include="number").columns if "hum" in c.lower()), None)

        if c_t and c_h and not df_t_local.empty and not df_h_local.empty:
            df_conf_directo = pd.DataFrame({
                "Temperatura": df_t_local[c_t],
                "Humedad": df_h_local[c_h]
            }).dropna()

            def evaluar_confort_dir(row):
                temp = row["Temperatura"]
                hum = row["Humedad"]
                if 20 <= temp <= 26 and 30 <= hum <= 60:
                    return "Confortable 🟢"
                elif temp > 26:
                    return "Caluroso / Seco 🔴" if hum < 40 else "Caluroso / Húmedo 🟠"
                else:
                    return "Frío / Fresco 🔵"

            df_conf_directo["Estado_Confort"] = df_conf_directo.apply(evaluar_confort_dir, axis=1)
            conteo_confort = df_conf_directo["Estado_Confort"].value_counts()

            cc1, cc2 = st.columns([1, 2])
            with cc1:
                st.markdown("**Distribución de Estados:**")
                st.dataframe(conteo_confort, use_container_width=True)

            with cc2:
                st.markdown("**Últimos registros evaluados:**")
                st.dataframe(df_conf_directo.tail(5), use_container_width=True)
        else:
            st.warning("No se pudieron enlazar automáticamente las columnas de temperatura y humedad para el cálculo.")

    # ----------------------------------------------------
    #  TAB 5 · Información del sitio
    # ----------------------------------------------------
    with tab5:
        st.markdown("### 🗺️ Información del Sitio de Medición y Mapa")

        col_map, col_info = st.columns([1, 1])

        with col_map:
            st.markdown("#### Ubicación Geográfica")
            eafit_location = pd.DataFrame({
                "lat": [6.2006],
                "lon": [-75.5783],
                "location": ["Universidad EAFIT"]
            })
            st.map(eafit_location, zoom=15, use_container_width=True)

        with col_info:
            st.markdown("#### Detalles del Nodo Sensor")
            st.markdown("""
                * **Institución:** Universidad EAFIT  
                * **Ubicación:** Medellín, Antioquia, Colombia  
                * **Coordenadas:** Lat: 6.2006, Lon: -75.5783  
                * **Altitud:** ~1,495 m s. n. m.  
                * **Hardware:** ESP32 + DHT22  
            """)
            st.markdown(f"- **Variables medidas:** " + ", ".join(f"`{v}`" for v in variables))
            st.markdown(f"- **Total de registros históricos:** `{len(df1)}`")
            if col_tiempo is not None and len(df1) > 0:
                st.markdown(f"- **Rango temporal:** `{df1.index.min():%Y-%m-%d %H:%M}` a `{df1.index.max():%Y-%m-%d %H:%M}`")

except FileNotFoundError as fnf_err:
    st.error("No se encontraron los archivos `hum.csv` y/o `temp.csv` en el directorio principal.")
    st.info("Por favor, sube `hum.csv` y `temp.csv` a la misma carpeta raíz de tu repositorio en GitHub donde se encuentra `Inicio.py`.")
except Exception as e:
    st.error(f"Error al procesar los archivos locales: {str(e)}")

# ============================================================
#  Pie de página profesional
# ============================================================
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #A0AEC0; font-size: 0.9rem; border-top: 1px solid #E9ECEF; margin-top: 3rem;">
        Desarrollado con Streamlit • Sistema IoT de Sensores Urbanos<br>
        Universidad EAFIT • Medellín, Colombia
    </div>
""", unsafe_allow_html=True)
