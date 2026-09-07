from pathlib import Path
import sys

import grpc
import pytest

# Soporte de importación independiente
ROOT_DIR = Path(__file__).resolve().parent.parent
for p in [str(ROOT_DIR), str(ROOT_DIR / "proto"), str(ROOT_DIR / "nodo_logico_grpc")]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import archivo_pb2
    import archivo_pb2_grpc
except ImportError:
    from proto import archivo_pb2, archivo_pb2_grpc


def test_conexion_grpc_caida():
    """Prueba de tolerancia a fallos cuando el servidor gRPC no está disponible."""
    # Puerto arbitrario donde no hay ningún servicio corriendo
    canal = grpc.insecure_channel('localhost:54999')
    cliente = archivo_pb2_grpc.MotorAnaliticaStub(canal)

    filtro = archivo_pb2.FiltroAnios(anio_inicio=2020, anio_fin=2020)

    # Con timeout corto para verificar captura de RpcError
    with pytest.raises(grpc.RpcError) as exc_info:
        cliente.ObtenerAgregacionInicial(filtro, timeout=1.5)

    error = exc_info.value
    assert error.code() in [
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.DEADLINE_EXCEEDED,
    ]


if __name__ == "__main__":
    print("Iniciando prueba de tolerancia a fallos...")
    try:
        test_conexion_grpc_caida()
        print("Tolerancia a fallos validada exitosamente.")
    except Exception as e:
        print(f"Resultado: {e}")
