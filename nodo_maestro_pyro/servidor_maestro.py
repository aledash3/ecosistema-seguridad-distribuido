import os
from pathlib import Path
import Pyro4
import pandas as pd

# Resolución dinámica de rutas absolutas independiente del CWD
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
RUTA_EXCEL = Path(os.getenv("DATA_EXCEL_PATH", DATA_DIR / "mdi_homicidiosintencionales_pm_2014_2025.xlsx"))
RUTA_CSV = Path(os.getenv("DATA_CSV_PATH", DATA_DIR / "dataset_procesado.csv"))
RUTA_SAMPLE_CSV = Path(os.getenv("DATA_SAMPLE_CSV_PATH", DATA_DIR / "sample_dataset.csv"))

COLUMNAS_UTILES = ['fecha_infraccion', 'tipo_muerte', 'provincia', 'arma']


@Pyro4.expose
class MaestroSeguridad:
    def __init__(self, ruta_archivo=None):
        self.ruta_archivo = ruta_archivo
        self.dataframe = self._cargar_y_preparar_datos()

    def _cargar_y_preparar_datos(self):
        """Carga solo lo esencial, optimizando memoria al máximo."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Si se pasó una ruta específica (e.g. en pruebas unitarias)
        if self.ruta_archivo and Path(self.ruta_archivo).exists():
            return self._cargar_csv(Path(self.ruta_archivo))

        # 2. Si existe el CSV ya procesado, cargarlo directamente
        if RUTA_CSV.exists():
            print(f"[INFO] Cargando CSV procesado existente: {RUTA_CSV}")
            return self._cargar_csv(RUTA_CSV)

        # 3. Si existe el Excel original, procesarlo y persistirlo como CSV
        if RUTA_EXCEL.exists():
            print(f"[INFO] Leyendo Excel original (Modo Optimizado de Memoria): {RUTA_EXCEL}")
            df_inicial = pd.read_excel(
                str(RUTA_EXCEL),
                sheet_name='1. Homicidios Intencionales',
                usecols=COLUMNAS_UTILES
            )

            print("[INFO] Procesando fechas y limpiando datos...")
            df_inicial['fecha_infraccion'] = pd.to_datetime(df_inicial['fecha_infraccion'], errors='coerce')
            df_inicial['Anio'] = df_inicial['fecha_infraccion'].dt.year
            df_inicial = df_inicial.dropna(subset=['Anio'])
            df_inicial['Anio'] = df_inicial['Anio'].astype(int)
            df_inicial = df_inicial.drop(columns=['fecha_infraccion'])

            # Normalizar textos
            for col in ['tipo_muerte', 'provincia', 'arma']:
                if col in df_inicial.columns:
                    df_inicial[col] = df_inicial[col].astype(str).str.strip().str.upper()

            print(f"[INFO] Guardando CSV ligero en: {RUTA_CSV}")
            df_inicial.to_csv(str(RUTA_CSV), sep=";", index=False, encoding="utf-8")
            return self._cargar_csv(RUTA_CSV)

        # 4. Si existe el dataset de muestra ligero, cargarlo
        if RUTA_SAMPLE_CSV.exists():
            print(f"[INFO] Dataset de producción no encontrado. Utilizando dataset de muestra: {RUTA_SAMPLE_CSV}")
            return self._cargar_csv(RUTA_SAMPLE_CSV)

        # 5. Fallback automático: Generar dataset de muestra si nada existe
        print("[AVISO] No se encontró ningún dataset. Generando dataset de muestra sintético...")
        from scripts.generate_sample_data import generar_dataset_muestra
        generar_dataset_muestra()
        return self._cargar_csv(RUTA_SAMPLE_CSV)

    def _cargar_csv(self, ruta: Path) -> pd.DataFrame:
        print("[INFO] Cargando dataset en memoria RAM con tipado categórico estricto...")
        tipos_optimizados = {
            'tipo_muerte': 'category',
            'provincia': 'category',
            'arma': 'category',
            'Anio': 'int16'
        }
        df = pd.read_csv(str(ruta), sep=";", dtype=tipos_optimizados)
        # Asegurar mayúsculas y limpieza
        for col in ['tipo_muerte', 'provincia', 'arma']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper().astype('category')
        return df

    def filtrar_por_anios(self, anio_inicio, anio_fin):
        """Filtra y devuelve los registros dentro del rango especificado."""
        df_filtrado = self.dataframe[(self.dataframe['Anio'] >= anio_inicio) &
                                     (self.dataframe['Anio'] <= anio_fin)]

        if df_filtrado.empty:
            return []

        return df_filtrado.to_dict(orient='records')

    def agregacion_inicial(self, anio_inicio, anio_fin):
        """Calcula el conteo de incidentes por categoría de muerte."""
        df_filtrado = self.dataframe[(self.dataframe['Anio'] >= anio_inicio) &
                                     (self.dataframe['Anio'] <= anio_fin)]

        if df_filtrado.empty:
            return {}

        return df_filtrado['tipo_muerte'].value_counts().to_dict()


def iniciar_servidor_pyro(host=None, port=None):
    host = host or os.getenv("PYRO_HOST", "0.0.0.0")
    port = int(port or os.getenv("PYRO_PORT", "0"))
    ns_host = os.getenv("PYRO_NS_HOST", None)

    daemon = Pyro4.Daemon(host=host, port=port)
    try:
        name_server = Pyro4.locateNS(host=ns_host)
        uri_maestro = daemon.register(MaestroSeguridad)
        name_server.register("maestro.seguridad", uri_maestro)
        print(f"[LISTO] Nodo Maestro registrado en Name Server como 'maestro.seguridad'. URI: {uri_maestro}")
        daemon.requestLoop()
    except Pyro4.errors.NamingError:
        print("[ERROR] No se pudo conectar al Name Server de Pyro4. Ejecute primero: python -m Pyro4.naming")
    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo Nodo Maestro Pyro4...")
        daemon.shutdown()


if __name__ == "__main__":
    iniciar_servidor_pyro()
