from io import StringIO
import os
from pathlib import Path
import sys

import grpc
import pandas as pd
import streamlit as st

# Soporte de importación de stubs gRPC
BASE_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent
PROTO_DIR = BASE_DIR / "proto"

for p in [str(DASHBOARD_DIR), str(PROTO_DIR), str(BASE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import archivo_pb2
    import archivo_pb2_grpc
except ImportError:
    from proto import archivo_pb2, archivo_pb2_grpc


DIRECCION_GRPC = os.getenv("GRPC_TARGET", "localhost:50051")
MAX_MESSAGE_LENGTH = 50 * 1024 * 1024  # 50 MB


@st.cache_resource
def crear_cliente_grpc(direccion=DIRECCION_GRPC):
    """Crea y cachea el stub de conexión gRPC para optimizar recursos en Streamlit."""
    opciones_red = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)
    ]
    canal = grpc.insecure_channel(direccion, options=opciones_red)
    return archivo_pb2_grpc.MotorAnaliticaStub(canal)


st.set_page_config(
    page_title="Dashboard Seguridad Nacional",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Dashboard de Seguridad Nacional Ecuador")
st.markdown("**Ecosistema Distribuido de Analítica (Pyro4 + gRPC + Streamlit)**")

# --- CONTROLES DE INTERACTIVIDAD Y FILTROS AVANZADOS ---
st.sidebar.header("🔍 Filtros de Tiempo")

tipo_filtro = st.sidebar.radio(
    "Seleccione el modo de búsqueda:",
    ("Todo el histórico (2014-2025)", "Últimos 5 años (2021-2025)", "Año específico", "Rango personalizado")
)

if tipo_filtro == "Todo el histórico (2014-2025)":
    anio_inicio, anio_fin = 2014, 2025
    st.sidebar.info("Mostrando datos de 2014 a 2025")
elif tipo_filtro == "Últimos 5 años (2021-2025)":
    anio_inicio, anio_fin = 2021, 2025
    st.sidebar.info("Mostrando datos de 2021 a 2025")
elif tipo_filtro == "Año específico":
    anio_unico = st.sidebar.selectbox("Seleccione el año:", list(range(2014, 2026)), index=10)
    anio_inicio, anio_fin = anio_unico, anio_unico
else:
    anio_inicio, anio_fin = st.sidebar.slider(
        "Deslice para seleccionar el rango:",
        min_value=2014, max_value=2025, value=(2014, 2025)
    )

st.sidebar.divider()
variable_visualizar = st.sidebar.selectbox(
    "📊 Variable a graficar en frecuencia:",
    ("Provincia", "Tipo de Arma")
)

# Objeto de petición gRPC tipado
filtro_rpc = archivo_pb2.FiltroAnios(anio_inicio=anio_inicio, anio_fin=anio_fin)
cliente = crear_cliente_grpc()

# --- MANEJO DE RED Y RENDERIZADO REACTIVO ---
try:
    # 1. Agregación Inicial (Tarjetas KPI)
    respuesta_agregacion = cliente.ObtenerAgregacionInicial(filtro_rpc)
    st.subheader(f"Resumen de Casos ({anio_inicio} - {anio_fin})")

    # Normalizar claves para evitar discrepancias de mayúsculas/minúsculas
    dict_agregacion = {
        str(item.categoria).strip().upper(): item.cantidad
        for item in respuesta_agregacion.datos
    }

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Homicidios", f'{dict_agregacion.get("HOMICIDIO", 0):,}')
    col2.metric("Asesinatos", f'{dict_agregacion.get("ASESINATO", 0):,}')
    col3.metric("Sicariatos", f'{dict_agregacion.get("SICARIATO", 0):,}')
    col4.metric("Femicidios", f'{dict_agregacion.get("FEMICIDIO", 0):,}')

    st.divider()

    # 2. Resumen de Tabla (Dataframe completo en RAM)
    st.subheader("Base de Datos Procesada")
    respuesta_tabla = cliente.ObtenerResumenTabla(filtro_rpc)

    if respuesta_tabla.total_registros > 0 and respuesta_tabla.json_dataframe and respuesta_tabla.json_dataframe != "[]":
        df_resumen = pd.read_json(StringIO(respuesta_tabla.json_dataframe))
        st.write(f"✅ **Total de registros encontrados:** {respuesta_tabla.total_registros:,}")
        st.dataframe(df_resumen, use_container_width=True, height=260)
    else:
        st.warning(f"No se registraron incidentes para el periodo {anio_inicio} - {anio_fin}.")

    st.divider()

    # 3. Gráficos Dinámicos de Distribución
    st.subheader(f"Distribución de casos por {variable_visualizar}")
    if variable_visualizar == "Provincia":
        respuesta_frec = cliente.ObtenerFrecuenciaProvincia(filtro_rpc)
    else:
        respuesta_frec = cliente.ObtenerFrecuenciaArma(filtro_rpc)

    df_frecuencias = pd.DataFrame([
        {"Categoría": item.categoria, "Cantidad": item.cantidad}
        for item in respuesta_frec.datos
    ])

    if not df_frecuencias.empty:
        df_frecuencias = df_frecuencias.sort_values(by="Cantidad", ascending=False)
        col_graf_1, col_graf_2 = st.columns([2, 1])

        with col_graf_1:
            st.bar_chart(data=df_frecuencias, x="Categoría", y="Cantidad", color="#ff4b4b")
        with col_graf_2:
            st.dataframe(df_frecuencias, hide_index=True, use_container_width=True)
    else:
        st.info("Gráfico no disponible por falta de datos en el rango seleccionado.")

except grpc.RpcError as e:
    st.error("🚨 **Error de Comunicación con el Nodo Lógico gRPC**")
    st.markdown(
        f"""
        > **Detalle técnico:** `{e.details() if hasattr(e, 'details') else e}`

        **Instrucciones para iniciar la arquitectura distribuida:**
        1. **Terminal 1**: Iniciar Name Server: `python -m Pyro4.naming`
        2. **Terminal 2**: Iniciar Nodo Maestro: `python nodo_maestro_pyro/servidor_maestro.py`
        3. **Terminal 3**: Iniciar Nodo Lógico gRPC: `python nodo_logico_grpc/servidor_grpc.py`
        4. **Terminal 4**: Iniciar Dashboard: `streamlit run dashboard_streamlit/app.py`
        """
    )
except Exception as e:
    st.error(f"Error inesperado en el dashboard: {str(e)}")
