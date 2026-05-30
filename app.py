import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Meteorológico METAR",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Dashboard Meteorológico METAR")
st.markdown("Carga un archivo CSV METAR para explorar indicadores meteorológicos.")

uploaded_file = st.file_uploader(
    "Seleccione un archivo CSV",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success(f"Archivo cargado correctamente ({len(df):,} registros)")

    # -------------------------
    # Conversión de fecha
    # -------------------------
    if "date_time" in df.columns:
        df["date_time"] = pd.to_datetime(
            df["date_time"],
            errors="coerce"
        )

    # -------------------------
    # Conversión numérica
    # -------------------------
    numeric_cols = [
        "air_temperature",
        "dew_point_temperature",
        "wind_speed",
        "wind_direction",
        "visibility",
        "air_pressure_at_sea_level",
        "cloud_coverage"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -------------------------
    # Sidebar filtros
    # -------------------------
    st.sidebar.header("Filtros")

    if "date_time" in df.columns:

        fecha_min = df["date_time"].min().date()
        fecha_max = df["date_time"].max().date()

        rango = st.sidebar.date_input(
            "Rango de fechas",
            [fecha_min, fecha_max]
        )

        if len(rango) == 2:
            inicio, fin = rango
            df = df[
                (df["date_time"].dt.date >= inicio)
                &
                (df["date_time"].dt.date <= fin)
            ]

    # ==========================
    # KPIs
    # ==========================

    st.subheader("Indicadores Principales")

    c1, c2, c3, c4 = st.columns(4)

    temp_prom = df["air_temperature"].mean()
    viento_prom = df["wind_speed"].mean()
    vis_prom = df["visibility"].mean()
    pres_prom = df["air_pressure_at_sea_level"].mean()

    c1.metric(
        "Temperatura Promedio",
        f"{temp_prom:.1f} °C"
    )

    c2.metric(
        "Viento Promedio",
        f"{viento_prom:.1f}"
    )

    c3.metric(
        "Visibilidad Promedio",
        f"{vis_prom:.0f}"
    )

    c4.metric(
        "Presión Promedio",
        f"{pres_prom:.1f}"
    )

    st.divider()

    # ==========================
    # Temperatura
    # ==========================

    col1, col2 = st.columns(2)

    with col1:

        fig_temp = px.line(
            df,
            x="date_time",
            y="air_temperature",
            color_discrete_sequence=px.colors.sequential.Viridis,
            title="Temperatura a lo largo del tiempo"
        )

        st.plotly_chart(
            fig_temp,
            use_container_width=True
        )

    with col2:

        fig_dew = px.line(
            df,
            x="date_time",
            y="dew_point_temperature",
            color_discrete_sequence=px.colors.sequential.Viridis,
            title="Punto de rocío"
        )

        st.plotly_chart(
            fig_dew,
            use_container_width=True
        )

    # ==========================
    # Viento
    # ==========================

    col1, col2 = st.columns(2)

    with col1:

        fig_wind = px.line(
            df,
            x="date_time",
            y="wind_speed",
            color_discrete_sequence=px.colors.sequential.Viridis,
            title="Velocidad del viento"
        )

        st.plotly_chart(
            fig_wind,
            use_container_width=True
        )

    with col2:

        wind_df = df[
            ["wind_direction", "wind_speed"]
        ].dropna()

        if len(wind_df) > 0:

            fig_rose = px.bar_polar(
                wind_df,
                r="wind_speed",
                theta="wind_direction",
                color="wind_speed",
                color_continuous_scale="Viridis",
                title="Rosa de los Vientos"
            )

            st.plotly_chart(
                fig_rose,
                use_container_width=True
            )

    st.divider()

    # ==========================
    # Distribuciones
    # ==========================

    col1, col2 = st.columns(2)

    with col1:

        fig_hist_temp = px.histogram(
            df,
            x="air_temperature",
            nbins=30,
            color_discrete_sequence=[
                px.colors.sequential.Viridis[5]
            ],
            title="Distribución de Temperaturas"
        )

        st.plotly_chart(
            fig_hist_temp,
            use_container_width=True
        )

    with col2:

        fig_hist_wind = px.histogram(
            df,
            x="wind_speed",
            nbins=30,
            color_discrete_sequence=[
                px.colors.sequential.Viridis[7]
            ],
            title="Distribución de Velocidad del Viento"
        )

        st.plotly_chart(
            fig_hist_wind,
            use_container_width=True
        )

    st.divider()

    # ==========================
    # Visibilidad y Presión
    # ==========================

    col1, col2 = st.columns(2)

    with col1:

        fig_vis = px.line(
            df,
            x="date_time",
            y="visibility",
            color_discrete_sequence=px.colors.sequential.Viridis,
            title="Visibilidad"
        )

        st.plotly_chart(
            fig_vis,
            use_container_width=True
        )

    with col2:

        fig_pres = px.line(
            df,
            x="date_time",
            y="air_pressure_at_sea_level",
            color_discrete_sequence=px.colors.sequential.Viridis,
            title="Presión Atmosférica"
        )

        st.plotly_chart(
            fig_pres,
            use_container_width=True
        )

    st.divider()

    # ==========================
    # Fenómenos Meteorológicos
    # ==========================

    if "current_wx1" in df.columns:

        wx = (
            df["current_wx1"]
            .fillna("Sin dato")
            .value_counts()
            .head(15)
            .reset_index()
        )

        wx.columns = [
            "Fenomeno",
            "Frecuencia"
        ]

        fig_wx = px.bar(
            wx,
            x="Fenomeno",
            y="Frecuencia",
            color="Frecuencia",
            color_continuous_scale="Viridis",
            title="Fenómenos Meteorológicos"
        )

        st.plotly_chart(
            fig_wx,
            use_container_width=True
        )

    # ==========================
    # Cobertura Nubosa
    # ==========================

    if "cloud_coverage" in df.columns:

        fig_cloud = px.histogram(
            df,
            x="cloud_coverage",
            nbins=20,
            color_discrete_sequence=[
                px.colors.sequential.Viridis[4]
            ],
            title="Cobertura Nubosa"
        )

        st.plotly_chart(
            fig_cloud,
            use_container_width=True
        )

    st.divider()

    st.subheader("Vista previa")

    st.dataframe(
        df.head(100),
        use_container_width=True
    )

else:

    st.info(
        "Cargue un archivo CSV METAR para comenzar."
    )
