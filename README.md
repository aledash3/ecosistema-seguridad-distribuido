# 🛡️ Ecosistema Distribuido de Analítica para la Seguridad Nacional

**Arquitectura distribuida de 3 capas para el procesamiento, análisis estadístico y visualización reactiva de homicidios intencionales en Ecuador (2014-2025) utilizando Pyro4, gRPC y Streamlit.**

[![CI](https://img.shields.io/github/actions/workflow/status/aledash3/ecosistema-seguridad-distribuido/ci.yml?branch=main&style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/aledash3/ecosistema-seguridad-distribuido/actions)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pyro4](https://img.shields.io/badge/Pyro4-Distributed%20Objects-orange?style=for-the-badge)](https://pyro4.readthedocs.io/)
[![gRPC](https://img.shields.io/badge/gRPC-Protocol%20Buffers-00bfa5?style=for-the-badge&logo=grpc&logoColor=white)](https://grpc.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Reactive%20Dashboard-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Optimized%20Analytics-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
![Licencia](https://img.shields.io/badge/Licencia-Acad%C3%A9mica%20y%20Educativa-blue?style=for-the-badge)

---

## 📌 Descripción General

El **Ecosistema Distribuido de Analítica para la Seguridad Nacional** es una solución de computación distribuida orientada a servicios (SOA) diseñada para procesar, filtrar y explorar grandes volúmenes de datos estadísticos oficiales sobre homicidios intencionales en Ecuador entre **2014 y 2025**.

El proyecto implementa principios clave de ingeniería de software backend y sistemas distribuidos:

* **Arquitectura de 3 Capas Desacopladas**: Separación estricta entre capa de persistencia en memoria, capa lógica/matemática intermedia y capa de presentación visual.
* **Comunicación Híbrida Especializada**:
  * **Pyro4 (Python Remote Objects)**: Invocación remota de métodos de alta velocidad para la capa interna de datos.
  * **gRPC + Protocol Buffers**: Transporte tipado, binario y de baja latencia entre el middleware lógico y el cliente visual con búfer ampliado a 50 MB.
* **Optimización Extrema de Memoria RAM**: Uso de tipos categóricos (`category`) en Pandas, selección de columnas críticas en la carga y tipado de enteros de bajo consumo (`int16`).
* **Resiliencia y Tolerancia a Fallos**: Verificación proactiva de canales, reconexión automática y degradación elegante ante la caída de nodos.
* **Visualización Reactiva**: Dashboard interactivo con métricas KPI, gráficos dinámicos de barras y exploración en tiempo real mediante **Streamlit**.

---

## 🏛️ Arquitectura del Sistema

```text
┌────────────────────────────────────────────────────────┐
│     Capa 3: Presentación Visual (Streamlit)            │
│     - Dashboard interactivo y KPIs                     │
│     - Filtros temporales y gráficos reactivos          │
│     - Cliente gRPC optimizado con @st.cache_resource   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼  gRPC (Protocol Buffers - Port 50051)
┌────────────────────────────────────────────────────────┐
│     Capa 2: Motor Lógico y Middleware (gRPC)           │
│     - Servidor gRPC (MotorAnaliticaServicer)           │
│     - Agregaciones estadísticas y ordenamiento         │
│     - Cliente Pyro4 con reconexión automática          │
│     - Serialización eficiente a JSON en memoria        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼  Pyro4 RPC (Name Server Lookup)
┌────────────────────────────────────────────────────────┐
│     Capa 1: Persistencia y Optimización RAM (Pyro4)    │
│     - Servidor Maestro (MaestroSeguridad)              │
│     - Reducción del uso de RAM (tipos category)        │
│     - Filtrado matricial de años                       │
│     - Soporte para dataset oficial o muestra sintética │
└────────────────────────────────────────────────────────┘
```

---

## 🗂️ Estructura del Proyecto

```text
ecosistema-seguridad-distribuido/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Pipeline de Integración Continua (Python 3.10, 3.11, 3.12)
├── data/
│   ├── sample_dataset.csv         # Dataset de muestra integrado (1200 registros listos para usar)
│   └── mdi_homicidiosintencionales_pm_2014_2025.xlsx  # Dataset oficial de producción (ignorado en Git)
├── dashboard_streamlit/
│   ├── app.py                     # Capa 3: Interfaz visual en Streamlit
│   ├── archivo_pb2.py             # Stubs generados por protoc
│   └── archivo_pb2_grpc.py        # Stubs generados por protoc
├── nodo_logico_grpc/
│   ├── servidor_grpc.py           # Capa 2: Servidor gRPC y cliente Pyro4
│   ├── archivo_pb2.py
│   └── archivo_pb2_grpc.py
├── nodo_maestro_pyro/
│   └── servidor_maestro.py        # Capa 1: Persistencia optimizada en RAM con Pyro4
├── proto/
│   ├── archivo.proto              # Contrato gRPC fuente de verdad
│   ├── archivo_pb2.py
│   └── archivo_pb2_grpc.py
├── scripts/
│   ├── compile_proto.py           # Script para compilar y sincronizar stubs protobuf
│   └── generate_sample_data.py    # Generador de datos sintéticos de prueba
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures y mocks de prueba
│   ├── test_ecosistema.py         # Prueba de tolerancia a caídas de gRPC
│   ├── test_grpc_servicer.py      # Pruebas unitarias de endpoints gRPC
│   ├── test_maestro.py            # Pruebas de carga, filtrado y tipos en el nodo maestro
│   └── test_proto.py              # Validación de serialización de mensajes protobuf
├── .gitignore
├── pyproject.toml                 # Metadatos del proyecto y configuración de herramientas
├── README.md                      # Documentación principal del sistema
└── requirements.txt               # Dependencias de producción y desarrollo
```

---

## ⚙️ Requisitos e Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/aledash3/ecosistema-seguridad-distribuido.git
cd ecosistema-seguridad-distribuido
```

### 2. Crear Entorno Virtual e Instalar Dependencias
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
.\venv\Scripts\activate
# En Linux / macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Dataset de Datos
* **Modo Demo Inmediato**: El repositorio incluye `data/sample_dataset.csv` con 1,200 registros realistas basados en provincias y modalidades de Ecuador. El sistema lo detecta y utiliza de inmediato sin descargas adicionales.
* **Modo Producción**: Si dispones del archivo oficial de la Policía Nacional / Ministerio del Interior (`mdi_homicidiosintencionales_pm_2014_2025.xlsx`), colócalo dentro de la carpeta `data/`. El nodo maestro lo procesará y optimizará automáticamente en su primer arranque.

---

## 🚀 Guía de Ejecución

Debido a su naturaleza distribuida, la arquitectura requiere **4 terminales independientes** ejecutadas en orden secuencial:

### 🖥️ Terminal 1 — Name Server de Pyro4
Inicia el registro dinámico de nombres para localización de servicios:
```bash
python -m Pyro4.naming
```

### 🖥️ Terminal 2 — Nodo Maestro Pyro4 (Capa 1)
Inicia el motor de datos y optimización de memoria:
```bash
python nodo_maestro_pyro/servidor_maestro.py
```
> Mensaje esperado: `[LISTO] Nodo Maestro registrado en Name Server como 'maestro.seguridad'.`

### 🖥️ Terminal 3 — Nodo Lógico gRPC (Capa 2)
Inicia el middleware computacional intermedio:
```bash
python nodo_logico_grpc/servidor_grpc.py
```
> Mensaje esperado: `[LISTO] Nodo Lógico gRPC ejecutándose en [::]:50051 (Canal Ampliado 50MB)...`

### 🖥️ Terminal 4 — Dashboard Streamlit (Capa 3)
Inicia la interfaz gráfica reactiva en el navegador:
```bash
streamlit run dashboard_streamlit/app.py
```
> Abrirá automáticamente en tu navegador `http://localhost:8501`.

---

## 🧩 Contrato gRPC (`proto/archivo.proto`)

El contrato de comunicación define 4 procedimientos remotos tipados:

```protobuf
syntax = "proto3";

package analitica_seguridad;

service MotorAnalitica {
  rpc ObtenerFrecuenciaProvincia (FiltroAnios) returns (RespuestaFrecuencias) {}
  rpc ObtenerFrecuenciaArma (FiltroAnios) returns (RespuestaFrecuencias) {}
  rpc ObtenerAgregacionInicial (FiltroAnios) returns (RespuestaFrecuencias) {}
  rpc ObtenerResumenTabla (FiltroAnios) returns (RespuestaTabla) {}
}

message FiltroAnios {
  int32 anio_inicio = 1;
  int32 anio_fin = 2;
}

message ItemFrecuencia {
  string categoria = 1;
  int32 cantidad = 2;
}

message RespuestaFrecuencias {
  repeated ItemFrecuencia datos = 1;
}

message RespuestaTabla {
  string json_dataframe = 1;
  int32 total_registros = 2;
}
```

Para recompilar y sincronizar automáticamente los stubs en todas las capas:
```bash
python scripts/compile_proto.py
```

---

## 🛡️ Técnicas de Optimización y Resiliencia

| Área | Técnica Implementada | Impacto |
| :--- | :--- | :--- |
| **Memoria RAM** | Conversión a tipo `category` en Pandas | Reducción de hasta el **85% de consumo de RAM** en columnas repetitivas |
| **Memoria RAM** | Tipado entero reducido (`int16`) para el año | Ahorro de espacio respecto a tipos `int64` |
| **Red** | Búfer gRPC de 50 MB (`grpc.max_send_message_length`) | Capacidad de transferir datasets grandes sin fragmentación de sockets |
| **Rendimiento UI** | `@st.cache_resource` en el stub gRPC | Elimina la sobrecarga de crear nuevos canales gRPC en cada clic del usuario |
| **Tolerancia a Fallos** | Captura estructurada de `grpc.RpcError` | La interfaz gráfica no colapsa si el backend no responde, guiando al usuario |
| **Portabilidad** | Rutas dinámicas con `pathlib.Path` | Ejecución válida desde cualquier directorio de trabajo o sistema operativo |

---

## 🧪 Pruebas Automatizadas y Calidad de Código

El proyecto cuenta con una suite de **17 pruebas unitarias e integrales** que validan:
* Carga de datos, tipado categórico y agregaciones estadísticas.
* Enrutamiento y serialización de endpoints gRPC con simulación de fallos.
* Integridad de contratos Protocol Buffers (`SerializeToString` / `ParseFromString`).
* Tolerancia ante la desconexión del servidor gRPC.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-9.1.1, pluggy-1.6.0
rootdir: ecosistema-seguridad-distribuido
collected 17 items

tests/test_ecosistema.py::test_conexion_grpc_caida PASSED                [  5%]
tests/test_grpc_servicer.py::test_grpc_obtener_frecuencia_provincia PASSED [ 11%]
tests/test_grpc_servicer.py::test_grpc_obtener_frecuencia_arma PASSED    [ 17%]
tests/test_grpc_servicer.py::test_grpc_obtener_agregacion_inicial PASSED [ 23%]
tests/test_grpc_servicer.py::test_grpc_obtener_resumen_tabla PASSED      [ 29%]
tests/test_grpc_servicer.py::test_grpc_rango_sin_datos PASSED            [ 35%]
tests/test_grpc_servicer.py::test_grpc_pyro_desconectado PASSED          [ 41%]
tests/test_maestro.py::test_maestro_carga_datos PASSED                   [ 47%]
tests/test_maestro.py::test_maestro_tipado_categorico PASSED             [ 52%]
tests/test_maestro.py::test_maestro_filtrar_por_anios_rango_valido PASSED [ 58%]
tests/test_maestro.py::test_maestro_filtrar_por_anios_sin_resultados PASSED [ 64%]
tests/test_maestro.py::test_maestro_agregacion_inicial PASSED            [ 70%]
tests/test_maestro.py::test_maestro_agregacion_inicial_rango_vacio PASSED [ 76%]
tests/test_proto.py::test_filtro_anios_proto PASSED                      [ 82%]
tests/test_proto.py::test_item_frecuencia_proto PASSED                   [ 88%]
tests/test_proto.py::test_respuesta_frecuencias_proto PASSED             [ 94%]
tests/test_proto.py::test_respuesta_tabla_proto PASSED                   [100%]

============================= 17 passed in 2.48s ==============================
```

### Ejecutar Pruebas Localmente
```bash
# Ejecutar todas las pruebas con reporte de cobertura
pytest --cov=. --cov-report=term-missing

# Ejecutar analizador de código estático (Linter)
ruff check .
```

### Integración Continua (GitHub Actions)
Cada `push` o `pull request` en la rama `main` ejecuta automáticamente las pruebas y el linter en **Python 3.10, 3.11 y 3.12** sobre máquinas virtuales Ubuntu.

---

## 👨‍💻 Autores

Este proyecto fue desarrollado de forma colaborativa por:

* **David Alejandro Cruz Palacios** — [@aledash3](https://github.com/aledash3)
* **Emily Mabel Ortega Constante** — [@BOOTEABLE](https://github.com/BOOTEABLE)
* **Carlos José Pilatuña Roldan** — [@Katsuro03](https://github.com/Katsuro03)

Carrera de Ingeniería en Ciencias de la Computación  
Asignatura: **Sistemas Distribuidos** (6to Semestre)  
**Universidad Politécnica Salesiana (UPS)**  
Quito, Ecuador

---

## 📜 Licencia

Este proyecto fue desarrollado con fines estrictamente académicos y de investigación formativa para la **Universidad Politécnica Salesiana (UPS)**.

Todos los derechos reservados conforme a las normativas de desarrollo académico e institucional. Prohibido su uso comercial no autorizado.
