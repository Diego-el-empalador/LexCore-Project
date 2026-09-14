"""Configuracion central del proyecto LexCore.

Autor: GPT-5.4
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCALA_JAR = BASE_DIR / "model" / "scala" / "target" / "scala-3.3.1" / "lexcore-scala.jar"
PROLOG_DIR = BASE_DIR / "model" / "prolog"
DATA_DIR = BASE_DIR / "model" / "data"

CONTRATOS_RAW = DATA_DIR / "contratos" / "contratos_raw.json"
CONTRATOS_PROC = DATA_DIR / "contratos" / "contratos_procesados.json"
HALLAZGOS_CSV = DATA_DIR / "resultados" / "hallazgos.csv"
AUDITORIAS_CSV = DATA_DIR / "resultados" / "auditorias.csv"
SESIONES_CSV = DATA_DIR / "sesiones" / "sesiones.csv"
LOTE_COMPARATIVO_CSV = DATA_DIR / "resultados" / "reporte_comparativo.csv"
TIPOS_CLAUSULA = DATA_DIR / "conocimiento" / "tipos_clausula.json"
NIVELES_RIESGO = DATA_DIR / "conocimiento" / "niveles_riesgo.json"
DATASET_CONTRATOS = DATA_DIR / "conocimiento" / "dataset_contratos.csv"

for _path in (
    CONTRATOS_RAW.parent,
    CONTRATOS_PROC.parent,
    HALLAZGOS_CSV.parent,
    AUDITORIAS_CSV.parent,
    SESIONES_CSV.parent,
    DATASET_CONTRATOS.parent,
):
    _path.mkdir(parents=True, exist_ok=True)
