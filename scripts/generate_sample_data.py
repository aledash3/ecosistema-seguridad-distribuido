from pathlib import Path
import pandas as pd
import random

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_CSV_PATH = DATA_DIR / "sample_dataset.csv"

PROVINCIAS = [
    "GUAYAS", "PICHINCHA", "MANABI", "LOS RIOS", "ESMERALDAS",
    "EL ORO", "AZUAY", "SANTO DOMINGO DE LOS TSACHILAS", "SANTA ELENA",
    "TUNGURAHUA", "CHIMBORAZO", "IMBABURA", "LOJA", "SUCUMBIOS"
]

TIPOS_MUERTE = ["ASESINATO", "HOMICIDIO", "SICARIATO", "FEMICIDIO"]
ARMAS = ["ARMA DE FUEGO", "ARMA BLANCA", "CONTUNDENTE", "ASFIXIA", "OTRA"]

def generar_dataset_muestra(num_registros=1200, random_seed=42):
    random.seed(random_seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    registros = []
    for _ in range(num_registros):
        anio = random.randint(2014, 2025)
        provincia = random.choices(
            PROVINCIAS,
            weights=[35, 20, 12, 10, 8, 5, 3, 2, 1.5, 1, 1, 0.5, 0.5, 0.5]
        )[0]
        tipo_muerte = random.choices(
            TIPOS_MUERTE,
            weights=[55, 25, 15, 5]
        )[0]
        arma = random.choices(
            ARMAS,
            weights=[70, 18, 6, 4, 2]
        )[0]
        registros.append({
            "tipo_muerte": tipo_muerte,
            "provincia": provincia,
            "arma": arma,
            "Anio": anio
        })

    df = pd.DataFrame(registros)
    df.to_csv(SAMPLE_CSV_PATH, sep=";", index=False, encoding="utf-8")
    print(f"[EXITO] Dataset de muestra generado con {len(df)} registros en: {SAMPLE_CSV_PATH}")
    return SAMPLE_CSV_PATH

if __name__ == "__main__":
    generar_dataset_muestra()
