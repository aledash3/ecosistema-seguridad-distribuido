import archivo_pb2


def test_filtro_anios_proto():
    filtro = archivo_pb2.FiltroAnios(anio_inicio=2015, anio_fin=2024)
    assert filtro.anio_inicio == 2015
    assert filtro.anio_fin == 2024

    serialized = filtro.SerializeToString()
    deserialized = archivo_pb2.FiltroAnios()
    deserialized.ParseFromString(serialized)
    assert deserialized.anio_inicio == 2015
    assert deserialized.anio_fin == 2024


def test_item_frecuencia_proto():
    item = archivo_pb2.ItemFrecuencia(categoria="PICHINCHA", cantidad=350)
    assert item.categoria == "PICHINCHA"
    assert item.cantidad == 350


def test_respuesta_frecuencias_proto():
    items = [
        archivo_pb2.ItemFrecuencia(categoria="GUAYAS", cantidad=500),
        archivo_pb2.ItemFrecuencia(categoria="MANABI", cantidad=200),
    ]
    resp = archivo_pb2.RespuestaFrecuencias(datos=items)
    assert len(resp.datos) == 2
    assert resp.datos[0].categoria == "GUAYAS"


def test_respuesta_tabla_proto():
    resp = archivo_pb2.RespuestaTabla(json_dataframe="[{\"id\": 1}]", total_registros=1)
    assert resp.total_registros == 1
    assert resp.json_dataframe == "[{\"id\": 1}]"
