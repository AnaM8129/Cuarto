import pandas as pd
import streamlit as st

# ============================================================
#  Configuración de la página
# ============================================================
st.set_page_config(
    page_title="AgroSmart IoT - EAFIT",
    page_icon="🌱",
    layout="wide"
)

# ============================================================
#  Estilos CSS · Dashboard Ejecutivo AgroSmart
#  Paleta: azul corporativo #0B2E4F · verde agro #15803D · verde hoja #DCFCE7
#          grises #F1F5F2 / #E2E8E4 / #5B6B63 · texto #0F172A
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --navy: #0B2E4F;
        --green: #15803D;
        --green-dark: #0F5B2E;
        --green-soft: #DCFCE7;
        --green-mist: #F0FDF4;
        --bg: #F1F5F2;
        --card: #FFFFFF;
        --line: #E2E8E4;
        --text: #0F172A;
        --muted: #5B6B63;
        --radius: 16px;
        --shadow-sm: 0 1px 2px rgba(11, 46, 79, 0.04), 0 4px 12px rgba(11, 46, 79, 0.05);
        --shadow-md: 0 2px 4px rgba(11, 46, 79, 0.05), 0 12px 28px rgba(11, 46, 79, 0.09);
    }

    /* ---------- Base ---------- */
    html, body, .stApp, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
        color: var(--text);
    }
    .stApp {
        background: var(--bg);
    }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    div.block-container {
        max-width: 1280px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* ---------- Encabezado principal ---------- */
    .main-header {
        position: relative;
        overflow: hidden;
        background: linear-gradient(120deg, #0B2E4F 0%, #0F5B54 55%, #15803D 100%);
        padding: 2.4rem 2.6rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
    }
    .main-header::after {
        content: "";
        position: absolute;
        right: -60px; top: -80px;
        width: 320px; height: 320px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 2rem;
        letter-spacing: -0.02em;
        margin: 0 0 0.45rem 0;
        padding: 0;
    }
    .main-header p {
        color: #CDE7D6 !important;
        font-size: 1.02rem;
        font-weight: 500;
        margin: 0;
        max-width: 760px;
    }
    .main-header .badge {
        display: inline-block;
        margin: 1.1rem 0.5rem 0 0;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.24);
        color: #FFFFFF;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ---------- Títulos ---------- */
    h3 {
        font-weight: 800 !important;
        letter-spacing: -0.015em;
        color: var(--navy) !important;
        padding-bottom: 0.4rem !important;
    }
    h4 {
        font-weight: 700 !important;
        color: var(--navy) !important;
        font-size: 1.05rem !important;
        margin-top: 1.2rem !important;
    }

    /* ---------- Nota contextual de cada sección ---------- */
    .section-note {
        background: var(--green-mist);
        border: 1px solid #BBF7D0;
        border-left: 4px solid var(--green);
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        color: #14532D;
        font-size: 0.93rem;
        font-weight: 500;
        line-height: 1.55;
        margin-bottom: 1.2rem;
    }
    .range-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin: 0.2rem 0 1.2rem 0;
    }
    .range-chips span {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 0.35rem 0.9rem;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--navy);
        box-shadow: var(--shadow-sm);
    }

    /* ---------- Pestañas ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: var(--card);
        padding: 8px;
        border-radius: var(--radius);
        border: 1px solid var(--line);
        box-shadow: var(--shadow-sm);
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        padding: 0 20px;
        background: transparent;
        border-radius: 11px;
        color: var(--muted);
        font-weight: 600;
        font-size: 0.93rem;
        border: none;
        transition: background 0.2s ease, color 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--green-mist);
        color: var(--green);
    }
    .stTabs [aria-selected="true"] {
        background: var(--green) !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 14px rgba(21, 128, 61, 0.28);
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.6rem;
    }

    /* ---------- Tarjetas de métricas ---------- */
    [data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-left: 4px solid var(--green);
        border-radius: var(--radius);
        padding: 1.1rem 1.3rem;
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-weight: 600;
        font-size: 0.85rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.9rem;
        font-weight: 800;
        color: var(--navy);
        letter-spacing: -0.02em;
    }

    /* ---------- Tablas y gráficos como tarjetas flotantes ---------- */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 6px;
        box-shadow: var(--shadow-sm);
        overflow: hidden;
    }
    [data-testid="stVegaLiteChart"],
    [data-testid="stArrowVegaLiteChart"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 1.2rem 1rem 0.8rem 1rem;
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stDeckGlJsonChart"],
    [data-testid="stMap"] {
        border-radius: var(--radius);
        overflow: hidden;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-sm);
    }

    /* ---------- Controles de entrada ---------- */
    [data-testid="stWidgetLabel"] p {
        font-weight: 600;
        color: var(--navy);
        font-size: 0.9rem;
    }
    div[data-baseweb="select"] > div {
        background: var(--card);
        border-radius: 12px;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-sm);
        min-height: 44px;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--green);
        box-shadow: 0 0 0 3px rgba(21, 128, 61, 0.16);
    }
    span[data-baseweb="tag"] {
        background: var(--green-soft) !important;
        color: #14532D !important;
        border-radius: 8px;
        font-weight: 600;
    }
    span[data-baseweb="tag"] span[role="presentation"] svg {
        fill: #14532D;
    }
    [data-testid="stSlider"] [role="slider"] {
        background: var(--green);
        box-shadow: 0 0 0 4px rgba(21, 128, 61, 0.2);
    }
    [data-testid="stCheckbox"] label p {
        font-weight: 500;
        color: var(--text);
    }

    /* ---------- Botones ---------- */
    .stDownloadButton button, .stButton button {
        background: var(--green);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.3rem;
        font-weight: 700;
        box-shadow: 0 6px 14px rgba(21, 128, 61, 0.26);
        transition: background 0.2s ease, transform 0.15s ease;
    }
    .stDownloadButton button:hover, .stButton button:hover {
        background: var(--navy);
        color: #FFFFFF;
        transform: translateY(-1px);
    }
    .stDownloadButton button:focus-visible, .stButton button:focus-visible {
        outline: 3px solid rgba(21, 128, 61, 0.4);
        outline-offset: 2px;
    }

    /* ---------- Alertas ---------- */
    [data-testid="stAlert"] {
        border-radius: 14px;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-sm);
    }

    /* ---------- Captions y listas ---------- */
    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }
    [data-testid="stMarkdownContainer"] ul {
        line-height: 1.9;
    }
    code {
        background: var(--green-mist);
        color: var(--green-dark);
        border-radius: 6px;
        padding: 0.1rem 0.4rem;
        font-weight: 600;
    }

    /* ---------- Pie de página ---------- */
    .app-footer {
        text-align: center;
        padding: 1.6rem 0 0.5rem 0;
        color: var(--muted);
        font-size: 0.88rem;
        font-weight: 500;
        border-top: 1px solid var(--line);
        margin-top: 3rem;
        line-height: 1.7;
    }
    .app-footer strong { color: var(--navy); }

    /* ---------- Responsive ---------- */
    @media (max-width: 768px) {
        .main-header { padding: 1.6rem 1.3rem; }
        .main-header h1 { font-size: 1.45rem; }
        .stTabs [data-baseweb="tab"] { padding: 0 14px; font-size: 0.85rem; }
    }
</style>
""", unsafe_allow_html=True)

# Nombres que se reconocen como columna de tiempo (sin importar mayúsculas)
CANDIDATAS_TIEMPO = ["time", "_time", "timestamp", "fecha", "date", "datetime", "Time"]


# ============================================================
#  Preparación de datos
# ============================================================
def preparar_datos(df):
    df = df.copy()
    col_tiempo = next(
        (c for c in df.columns if str(c).strip().lower() in [cand.lower() for cand in CANDIDATAS_TIEMPO]),
        None
    )
    if col_tiempo is not None:
        df[col_tiempo] = pd.to_datetime(df[col_tiempo], errors="coerce")
        df = df.dropna(subset=[col_tiempo]).set_index(col_tiempo).sort_index()
        df.index.name = "Time"

    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            convertida = pd.to_numeric(
                df[c].astype(str).str.replace(",", ".", regex=False),
                errors="coerce"
            )
            if convertida.notna().mean() >= 0.9:
                df[c] = convertida

    numericas = df.select_dtypes(include="number").columns.tolist()
    return df, numericas, col_tiempo


def normalizar(df):
    rango = (df.max() - df.min()).replace(0, 1)
    return (df - df.min()) / rango


# ============================================================
#  Encabezado Visual Moderno (Banner)
# ============================================================
st.markdown("""
    <div class="main-header">
        <h1>🌱 AgroSmart IoT: Monitoreo y Automatización Climática</h1>
        <p>Invernadero y cultivos protegidos: seguimiento continuo de temperatura y humedad
        para anticipar el estrés de las plantas y apoyar la ventilación automatizada •
        Universidad EAFIT</p>
        <span class="badge">🌡️ Temperatura y humedad relativa</span>
        <span class="badge">🌬️ Ventilación y compuertas automatizadas</span>
        <span class="badge">📡 ESP32 + DHT22</span>
    </div>
""", unsafe_allow_html=True)

# ============================================================
#  Carga automática de hum.csv y temp.csv
# ============================================================
try:
    df_hum_raw = pd.read_csv("hum.csv")
    df_temp_raw = pd.read_csv("temp.csv")

    df_hum, vars_hum, col_t_hum = preparar_datos(df_hum_raw)
    df_temp, vars_temp, col_t_temp = preparar_datos(df_temp_raw)

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
        f"✅ Telemetría del invernadero cargada correctamente. Variables climáticas detectadas: "
        + ", ".join(f"`{v}`" for v in variables)
    )

    # Pestañas principales con nuevo diseño
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Monitoreo Climático", "📊 Estadísticas del Cultivo", "🔍 Filtros", "🌱 Viabilidad Climática", "🏡 Información del Invernadero"]
    )

    # ----------------------------------------------------
    #  TAB 1 · Monitoreo Climático
    # ----------------------------------------------------
    with tab1:
        st.markdown("### 📈 Monitoreo Climático del Invernadero")
        st.markdown(
            '<div class="section-note">Evolución en el tiempo de las lecturas del nodo sensor. '
            'Úsala para detectar picos de calor o humedad que justifiquen abrir compuertas y activar la ventilación.</div>',
            unsafe_allow_html=True
        )
        
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
    #  TAB 2 · Estadísticas del Cultivo
    # ----------------------------------------------------
    with tab2:
        st.markdown("### 📊 Estadísticas del Microclima del Cultivo")
        st.markdown(
            '<div class="section-note">Resumen de las condiciones registradas dentro del invernadero. '
            'Un promedio estable y una baja variabilidad indican un microclima controlado; picos y valles marcados señalan '
            'momentos de estrés para las plantas.</div>',
            unsafe_allow_html=True
        )

        st.markdown("#### Descriptivas Generales")
        st.dataframe(df1[variables].describe().T.round(2), use_container_width=True)

        st.markdown("#### Detalle por Variable")
        var_stats = st.selectbox("Seleccione variable para métricas", variables, key="var_stats")
        serie = df1[var_stats].dropna()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio del periodo", f"{serie.mean():.2f}")
        m2.metric("Pico máximo", f"{serie.max():.2f}")
        m3.metric("Valle mínimo", f"{serie.min():.2f}")
        m4.metric("Variabilidad (desv. est.)", f"{serie.std():.2f}")

        if len(variables) >= 2:
            st.markdown("#### Relación entre Variables Climáticas")
            st.dataframe(df1[variables].corr().round(2), use_container_width=True)
            st.caption("Valores cercanos a 1 o −1 indican una relación lineal fuerte (por ejemplo, cómo cambia la humedad al subir la temperatura); cercanos a 0, poca relación.")

    # ----------------------------------------------------
    #  TAB 3 · Filtros
    # ----------------------------------------------------
    with tab3:
        st.markdown("### 🔍 Filtrado de Lecturas del Invernadero")
        st.markdown(
            '<div class="section-note">Aísla las lecturas dentro de un rango de valores para revisar episodios concretos '
            '(por ejemplo, horas con temperatura alta) y descárgalos para tu análisis agronómico.</div>',
            unsafe_allow_html=True
        )

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
    #  TAB 4 · Índice de Viabilidad Climática para Cultivos
    # ----------------------------------------------------
    with tab4:
        st.markdown("### 🌱 Índice de Viabilidad Climática para Cultivos")
        st.markdown(
            '<div class="section-note">Clasifica cada lectura según su cercanía al rango óptimo del cultivo y detecta '
            'estrés térmico o humedad fuera de rango. Un porcentaje alto de lecturas fuera del rango óptimo '
            'es la señal para reforzar la ventilación y el control de compuertas.</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="range-chips">'
            '<span>🟢 Rango óptimo: 20–26 °C</span>'
            '<span>💧 Humedad relativa óptima: 30–60 %</span>'
            '<span>🔴 Estrés térmico: &gt; 26 °C</span>'
            '</div>',
            unsafe_allow_html=True
        )

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
                    return "Óptimo para el cultivo 🟢"
                elif temp > 26:
                    return "Estrés térmico / Aire seco 🔴" if hum < 40 else "Estrés térmico / Humedad alta 🟠"
                else:
                    return "Fresco o humedad fuera de rango 🔵"

            df_conf_directo["Estado_Confort"] = df_conf_directo.apply(evaluar_confort_dir, axis=1)
            conteo_confort = df_conf_directo["Estado_Confort"].value_counts()

            cc1, cc2 = st.columns([1, 2])
            with cc1:
                st.markdown("**Distribución de la Viabilidad Climática:**")
                st.dataframe(conteo_confort, use_container_width=True)

            with cc2:
                st.markdown("**Últimas lecturas evaluadas:**")
                st.dataframe(df_conf_directo.tail(5), use_container_width=True)
        else:
            st.warning("No se pudieron enlazar automáticamente las columnas de temperatura y humedad para calcular el índice de viabilidad climática.")

    # ----------------------------------------------------
    #  TAB 5 · Información del invernadero
    # ----------------------------------------------------
    with tab5:
        st.markdown("### 🏡 Información del Invernadero y Sistema de Control")
        st.markdown(
            '<div class="section-note">Ubicación del sitio de medición y descripción del sistema AgroSmart IoT: '
            'sensores de microclima y actuadores para la ventilación automatizada.</div>',
            unsafe_allow_html=True
        )

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
            st.markdown("#### Detalles del Nodo AgroSmart")
            st.markdown("""
                * **Proyecto:** AgroSmart IoT · Cultivos protegidos  
                * **Institución:** Universidad EAFIT  
                * **Ubicación:** Medellín, Antioquia, Colombia  
                * **Coordenadas:** Lat: 6.2006, Lon: -75.5783  
                * **Altitud:** ~1,495 m s. n. m.  
                * **Sensores:** ESP32 + DHT22 (temperatura y humedad relativa)  
                * **Ventilación automatizada:** servo para el control de compuertas del invernadero  
                * **Indicador de estado:** LED asociado al sistema de ventilación  
            """)
            st.markdown(f"- **Variables climáticas medidas:** " + ", ".join(f"`{v}`" for v in variables))
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
    <div class="app-footer">
        Desarrollado con Streamlit • AgroSmart IoT: Monitoreo y Automatización Climática para Cultivos Protegidos<br>
        <strong>Universidad EAFIT</strong> • Medellín, Colombia
    </div>
""", unsafe_allow_html=True)
