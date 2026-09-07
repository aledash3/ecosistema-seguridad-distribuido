from concurrent import futures
import os
from pathlib import Path
import sys

import grpc
import pandas as pd
import Pyro4

# Soporte de importación tanto desde la raíz del proyecto como desde nodo_logico_grpc/
BASE_DIR = Path(__file__).resolve().parent.parent
NODO_DIR = Path(__file__).resolve().parent
PROTO_DIR = BASE_DIR / "proto"

for p in [str(NODO_DIR), str(PROTO_DIR), str(BASE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import archivo_pb2
    import archivo_pb2_grpc
except ImportError:
    from proto import archivo_pb2, archivo_pb2_grpc


PYRO_SERVICE_NAME = os.getenv("PYRO_SERVICE_NAME", "maestro.seguridad")
GRPC_HOST = os.getenv("GRPC_HOST", "[::]")
GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))
MAX_MESSAGE_LENGTH = 50 * 1024 * 1024  # 50 MB


class MotorAnaliticaServicer(archivo_pb2_grpc.MotorAnaliticaServicer):
    def __init__(self, cliente_pyro=None):
        self._cliente_pyro = cliente_pyro

    @property
    def cliente_pyro(self):
        if self._cliente_pyro is None:
            self._cliente_pyro = Pyro4.Proxy(f"PYRONAME:{PYRO_SERVICE_NAME}")
        return self._cliente_pyro

    def _verificar_conexion_pyro(self, context):
        try:
            self.cliente_pyro._pyroBind()
        except Exception as error:
            print(f"[ERROR] Conexión con Pyro4 falló: {error}")
            context.abort(grpc.StatusCode.UNAVAILABLE, f"Nodo Maestro Pyro4 no responde ({error})")

    def _procesar_frecuencia(self, request, context, columna_objetivo):
        self._verificar_conexion_pyro(context)
        try:
            datos_brutos = self.cliente_pyro.filtrar_por_anios(request.anio_inicio, request.anio_fin)
            df = pd.DataFrame(datos_brutos)

            if df.empty or columna_objetivo not in df.columns:
                return archivo_pb2.RespuestaFrecuencias(datos=[])

            conteo = df[columna_objetivo].value_counts()
            lista_items = [
                archivo_pb2.ItemFrecuencia(categoria=str(k), cantidad=int(v))
                for k, v in conteo.items()
            ]

            return archivo_pb2.RespuestaFrecuencias(datos=lista_items)
        except grpc.RpcError:
            raise
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error calculando frecuencias: {str(e)}")

    def ObtenerFrecuenciaProvincia(self, request, context):
        return self._procesar_frecuencia(request, context, 'provincia')

    def ObtenerFrecuenciaArma(self, request, context):
        return self._procesar_frecuencia(request, context, 'arma')

    def ObtenerAgregacionInicial(self, request, context):
        self._verificar_conexion_pyro(context)
        try:
            conteo = self.cliente_pyro.agregacion_inicial(request.anio_inicio, request.anio_fin)
            if not conteo:
                return archivo_pb2.RespuestaFrecuencias(datos=[])

            lista_items = [
                archivo_pb2.ItemFrecuencia(categoria=str(k).upper(), cantidad=int(v))
                for k, v in conteo.items()
            ]
            return archivo_pb2.RespuestaFrecuencias(datos=lista_items)
        except grpc.RpcError:
            raise
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error obteniendo agregación inicial: {str(e)}")

    def ObtenerResumenTabla(self, request, context):
        self._verificar_conexion_pyro(context)
        try:
            datos_brutos = self.cliente_pyro.filtrar_por_anios(request.anio_inicio, request.anio_fin)
            df = pd.DataFrame(datos_brutos)

            if df.empty:
                return archivo_pb2.RespuestaTabla(json_dataframe="[]", total_registros=0)

            json_df = df.to_json(orient='records')
            return archivo_pb2.RespuestaTabla(json_dataframe=json_df, total_registros=len(df))
        except grpc.RpcError:
            raise
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error serializando tabla: {str(e)}")


def crear_servidor_grpc(servicer=None, puerto=GRPC_PORT, host=GRPC_HOST):
    opciones_red = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)
    ]
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=opciones_red)
    instancia_servicer = servicer or MotorAnaliticaServicer()
    archivo_pb2_grpc.add_MotorAnaliticaServicer_to_server(instancia_servicer, servidor)
    direccion = f'{host}:{puerto}'
    servidor.add_insecure_port(direccion)
    return servidor, direccion


def iniciar_servidor_grpc():
    servidor, direccion = crear_servidor_grpc()
    print(f"[LISTO] Nodo Lógico gRPC ejecutándose en {direccion} (Canal Ampliado 50MB)...")
    servidor.start()
    try:
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo servidor gRPC...")
        servidor.stop(0)


if __name__ == '__main__':
    iniciar_servidor_grpc()
