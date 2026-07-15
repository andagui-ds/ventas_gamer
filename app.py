import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página para que use pantalla ancha (Wide) y título en la pestaña
st.set_page_config(
    page_title="Mi Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal del Dashboard con estilo
st.markdown("""
    <div style="text-align: left; margin-bottom: 20px;">
        <h1 style="margin-bottom: 5px;">📊 Mi Dashboard de Ventas</h1>
        <p style="color: #666; font-size: 16px;">📈 Análisis Interactivo Completo (Cool Version)</p>
    </div>
""", unsafe_allow_html=True)

# 1. Cargar y preparar los datos


@st.cache_data
def load_data():
    df = pd.read_csv("data/datos.csv")
    # Convertir la columna fecha a formato datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df


try:
    df_raw = load_data()

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.markdown("### 🛠️ Filtros Interactivos")

    # Filtro de categorías
    categorias_disponibles = sorted(df_raw['categoria'].unique())
    categorias_seleccionadas = st.sidebar.multiselect(
        "Filtrar por Categoría",
        options=categorias_disponibles,
        default=categorias_disponibles
    )

    # Filtro de rango de fechas
    min_date = df_raw['fecha'].min().to_pydatetime()
    max_date = df_raw['fecha'].max().to_pydatetime()

    rango_fechas = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Aplicar filtros al DataFrame
    df_filtrado = df_raw[df_raw['categoria'].isin(categorias_seleccionadas)]

    # Asegurar que se seleccionó un rango de fechas válido antes de filtrar
    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        inicio, fin = pd.to_datetime(
            rango_fechas[0]), pd.to_datetime(rango_fechas[1])
        df_filtrado = df_filtrado[(df_filtrado['fecha'] >= inicio) & (
            df_filtrado['fecha'] <= fin)]

    # --- CÁLCULO DE MÉTRICAS (KPIs) ---
    total_ventas = df_filtrado['total_final'].sum()
    unidades_vendidas = df_filtrado['cantidad'].sum()
    monto_promedio = df_filtrado['total_final'].mean(
    ) if not df_filtrado.empty else 0
    total_transacciones = len(df_filtrado)

    # --- RENDERIZADO DE KPIs EN COLUMNAS ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Ventas Totales ($)",
            value=f"$ {total_ventas:,.2f}"
        )
    with col2:
        st.metric(
            label="Unidades Vendidas",
            value=f"{unidades_vendidas:,}"
        )
    with col3:
        st.metric(
            label="Monto Promedio por Venta",
            value=f"$ {monto_promedio:,.2f}"
        )
    with col4:
        st.metric(
            label="Transacciones",
            value=f"{total_transacciones:,}"
        )

    st.markdown("---")  # Línea divisoria

    # --- SECCIÓN DE GRÁFICOS (2 Columnas) ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("Ventas Totales por Categoría")
        if not df_filtrado.empty:
            # Agrupar ventas por categoría
            ventas_por_cat = df_filtrado.groupby(
                'categoria')['total_final'].sum().reset_index()
            # Ordenar para que se vea mejor
            ventas_por_cat = ventas_por_cat.sort_values(
                by='total_final', ascending=False)

            # Gráfico de barras nativo de Streamlit
            st.bar_chart(
                data=ventas_por_cat,
                x='categoria',
                y='total_final',
                color='#1f77b4',  # Azul elegante
                use_container_width=True
            )
        else:
            st.info("No hay datos para mostrar en este rango/categoría.")

    with col_der:
        st.subheader("Evolución de Ventas Diarias")
        if not df_filtrado.empty:
            # Agrupar ventas por fecha
            ventas_diarias = df_filtrado.groupby(
                'fecha')['total_final'].sum().reset_index()
            ventas_diarias = ventas_diarias.sort_values('fecha')

            # Gráfico de área nativo de Streamlit
            st.area_chart(
                data=ventas_diarias,
                x='fecha',
                y='total_final',
                color='#2ca02c',  # Verde suave elegante
                use_container_width=True
            )
        else:
            st.info("No hay datos para mostrar en este rango/categoría.")

    st.markdown("---")

    # --- TABLA DE DATOS COLAPSABLE ---
    with st.expander("📝 Ver Resumen de Datos (Últimas Transacciones)"):
        st.success("¡Datos filtrados con éxito!")
        # Mostrar la tabla formateando la fecha a string simple
        df_mostrar = df_filtrado.copy()
        df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%Y-%m-%d')
        st.dataframe(df_mostrar, use_container_width=True)

except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'data/datos.csv'. Asegúrate de haber guardado el archivo CSV generado anteriormente dentro de una carpeta llamada 'data'.")
except Exception as e:
    st.error(f"❌ Ocurrió un error inesperado: {e}")
