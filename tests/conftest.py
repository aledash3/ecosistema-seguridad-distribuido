from pathlib import Path
import sys
import pytest

# Configurar PYTHONPATH para todos los módulos
ROOT_DIR = Path(__file__).resolve().parent.parent
for p in [str(ROOT_DIR), str(ROOT_DIR / "proto"), str(ROOT_DIR / "nodo_logico_grpc"), str(ROOT_DIR / "nodo_maestro_pyro"), str(ROOT_DIR / "dashboard_streamlit")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from nodo_maestro_pyro.servidor_maestro import MaestroSeguridad


@pytest.fixture(scope="session")
def dataset_muestra_path():
    p = ROOT_DIR / "data" / "sample_dataset.csv"
    if not p.exists():
        from scripts.generate_sample_data import generar_dataset_muestra
        generar_dataset_muestra()
    return p


@pytest.fixture(scope="session")
def maestro_instancia(dataset_muestra_path):
    return MaestroSeguridad(ruta_archivo=str(dataset_muestra_path))


class MockPyroCliente:
    def __init__(self, maestro):
        self.maestro = maestro
        self.bind_fails = False

    def _pyroBind(self):
        if self.bind_fails:
            raise RuntimeError("Error simulado de conexión con Pyro4 Name Server")
        return True

    def filtrar_por_anios(self, anio_inicio, anio_fin):
        return self.maestro.filtrar_por_anios(anio_inicio, anio_fin)

    def agregacion_inicial(self, anio_inicio, anio_fin):
        return self.maestro.agregacion_inicial(anio_inicio, anio_fin)


@pytest.fixture
def mock_pyro_cliente(maestro_instancia):
    return MockPyroCliente(maestro_instancia)


class MockGrpcContext:
    def __init__(self):
        self.aborted = False
        self.code = None
        self.details = None

    def abort(self, code, details):
        self.aborted = True
        self.code = code
        self.details = details
        raise RuntimeError(f"gRPC Abort [{code}]: {details}")


@pytest.fixture
def mock_grpc_context():
    return MockGrpcContext()
