import pandas as pd


def test_maestro_carga_datos(maestro_instancia):
    df = maestro_instancia.dataframe
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "tipo_muerte" in df.columns
    assert "provincia" in df.columns
    assert "arma" in df.columns
    assert "Anio" in df.columns


def test_maestro_tipado_categorico(maestro_instancia):
    df = maestro_instancia.dataframe
    # Validar que los campos de texto usen categoría para optimizar memoria RAM
    assert df["tipo_muerte"].dtype.name == "category"
    assert df["provincia"].dtype.name == "category"
    assert df["arma"].dtype.name == "category"


def test_maestro_filtrar_por_anios_rango_valido(maestro_instancia):
    registros = maestro_instancia.filtrar_por_anios(2020, 2022)
    assert isinstance(registros, list)
    assert len(registros) > 0

    for r in registros:
        assert 2020 <= r["Anio"] <= 2022
        assert isinstance(r["tipo_muerte"], str)
        assert isinstance(r["provincia"], str)


def test_maestro_filtrar_por_anios_sin_resultados(maestro_instancia):
    registros = maestro_instancia.filtrar_por_anios(1900, 1910)
    assert registros == []


def test_maestro_agregacion_inicial(maestro_instancia):
    conteo = maestro_instancia.agregacion_inicial(2014, 2025)
    assert isinstance(conteo, dict)
    assert len(conteo) > 0

    # Categorías esperadas
    for cat in ["ASESINATO", "HOMICIDIO"]:
        assert cat in conteo
        assert conteo[cat] >= 0


def test_maestro_agregacion_inicial_rango_vacio(maestro_instancia):
    conteo = maestro_instancia.agregacion_inicial(2090, 2100)
    assert conteo == {}
