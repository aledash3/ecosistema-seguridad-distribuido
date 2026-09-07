import pytest
import grpc
import json
from nodo_logico_grpc.servidor_grpc import MotorAnaliticaServicer
import archivo_pb2


def test_grpc_obtener_frecuencia_provincia(mock_pyro_cliente, mock_grpc_context):
    servicer = MotorAnaliticaServicer(cliente_pyro=mock_pyro_cliente)
    request = archivo_pb2.FiltroAnios(anio_inicio=2014, anio_fin=2025)

    respuesta = servicer.ObtenerFrecuenciaProvincia(request, mock_grpc_context)
    assert isinstance(respuesta, archivo_pb2.RespuestaFrecuencias)
    assert len(respuesta.datos) > 0

    # Verificar que contenga provincias esperadas
    categorias = [item.categoria for item in respuesta.datos]
    assert any("GUAYAS" in c or "PICHINCHA" in c for c in categorias)
    assert all(item.cantidad > 0 for item in respuesta.datos)


def test_grpc_obtener_frecuencia_arma(mock_pyro_cliente, mock_grpc_context):
    servicer = MotorAnaliticaServicer(cliente_pyro=mock_pyro_cliente)
    request = archivo_pb2.FiltroAnios(anio_inicio=2014, anio_fin=2025)

    respuesta = servicer.ObtenerFrecuenciaArma(request, mock_grpc_context)
    assert isinstance(respuesta, archivo_pb2.RespuestaFrecuencias)
    assert len(respuesta.datos) > 0

    categorias = [item.categoria for item in respuesta.datos]
    assert any("FUEGO" in c or "BLANCA" in c for c in categorias)


def test_grpc_obtener_agregacion_inicial(mock_pyro_cliente, mock_grpc_context):
    servicer = MotorAnaliticaServicer(cliente_pyro=mock_pyro_cliente)
    request = archivo_pb2.FiltroAnios(anio_inicio=2014, anio_fin=2025)

    respuesta = servicer.ObtenerAgregacionInicial(request, mock_grpc_context)
    assert isinstance(respuesta, archivo_pb2.RespuestaFrecuencias)
    assert len(respuesta.datos) > 0

    categorias = [item.categoria for item in respuesta.datos]
    assert "ASESINATO" in categorias or "HOMICIDIO" in categorias


def test_grpc_obtener_resumen_tabla(mock_pyro_cliente, mock_grpc_context):
    servicer = MotorAnaliticaServicer(cliente_pyro=mock_pyro_cliente)
    request = archivo_pb2.FiltroAnios(anio_inicio=2020, anio_fin=2022)

    respuesta = servicer.ObtenerResumenTabla(request, mock_grpc_context)
    assert isinstance(respuesta, archivo_pb2.RespuestaTabla)
    assert respuesta.total_registros > 0

    datos = json.loads(respuesta.json_dataframe)
    assert isinstance(datos, list)
    assert len(datos) == respuesta.total_registros


def test_grpc_rango_sin_datos(mock_pyro_cliente, mock_grpc_context):
    servicer = MotorAnaliticaServicer(cliente_pyro=mock_pyro_cliente)
    request = archivo_pb2.FiltroAnios(anio_inicio=1900, anio_fin=1910)

    resp_frec = servicer.ObtenerFrecuenciaProvincia(request, mock_grpc_context)
    assert len(resp_frec.datos) == 0

    resp_tabla = servicer.ObtenerResumenTabla(request, mock_grpc_context)
    assert resp_tabla.total_registros == 0
    assert resp_tabla.json_dataframe == "[]"


def test_grpc_pyro_desconectado(mock_pyro_cliente, mock_grpc_context):
    mock_pyro_cliente.bind_fails = True
    servicer = MotorAnaliticaServicer(cliente_pyro=mock_pyro_cliente)
    request = archivo_pb2.FiltroAnios(anio_inicio=2020, anio_fin=2020)

    with pytest.raises(RuntimeError):
        servicer.ObtenerAgregacionInicial(request, mock_grpc_context)

    assert mock_grpc_context.aborted is True
    assert mock_grpc_context.code == grpc.StatusCode.UNAVAILABLE
