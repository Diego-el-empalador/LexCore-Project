"""Persistencia tabular de hallazgos, auditorias y reportes comparativos.

Autor: GPT-5.4
"""

from __future__ import annotations

import csv
import pandas as pd

from controller.utils.config import AUDITORIAS_CSV, HALLAZGOS_CSV, LOTE_COMPARATIVO_CSV
from controller.utils.logger import get_logger

logger = get_logger(__name__)

_COLUMNAS_AUDITORIA = [
    "auditoria_id",
    "contrato_id",
    "fecha",
    "total_clausulas",
    "clausulas_riesgo",
    "resultado",
    "score",
    "nivel_riesgo",
    "nombre",
    "categoria",
    "motor_riesgo",
    "fuente_tokenizacion",
]


def leer_hallazgos() -> pd.DataFrame:
    if not HALLAZGOS_CSV.exists():
        return pd.DataFrame(
            columns=[
                "contrato_id",
                "clausula_id",
                "tipo_riesgo",
                "severidad",
                "articulo_violado",
                "descripcion_riesgo",
                "fecha",
            ]
        )
    return pd.read_csv(HALLAZGOS_CSV, on_bad_lines="skip", engine="python")


def guardar_hallazgos(contrato_id: str, hallazgos: list[dict]) -> None:
    if not hallazgos:
        return
    df = pd.DataFrame(hallazgos)
    df["contrato_id"] = contrato_id
    df.to_csv(HALLAZGOS_CSV, mode="a", header=not HALLAZGOS_CSV.exists(), index=False)


def eliminar_hallazgos(contrato_id: str) -> None:
    if not HALLAZGOS_CSV.exists():
        return
    df = pd.read_csv(HALLAZGOS_CSV)
    df = df[df["contrato_id"] != contrato_id]
    df.to_csv(HALLAZGOS_CSV, index=False)


def leer_auditorias() -> pd.DataFrame:
    if not AUDITORIAS_CSV.exists():
        return pd.DataFrame(columns=_COLUMNAS_AUDITORIA)
    filas = _leer_auditorias_normalizadas()
    df = pd.DataFrame(filas, columns=_COLUMNAS_AUDITORIA)
    if not df.empty:
        df = df.dropna(how="all")
        df = df[df["contrato_id"].notna()]
        df = df[df["contrato_id"].astype(str).str.strip() != ""]
    _escribir_auditorias(df)
    return df.reset_index(drop=True)


def guardar_auditoria(auditoria: dict) -> None:
    existentes = leer_auditorias()
    if not existentes.empty and auditoria.get("contrato_id") in set(existentes["contrato_id"].astype(str)):
        existentes = existentes[existentes["contrato_id"].astype(str) != str(auditoria.get("contrato_id"))]
        existentes = pd.concat([existentes, pd.DataFrame([_normalizar_auditoria(auditoria)])], ignore_index=True)
        _escribir_auditorias(existentes)
    else:
        existentes = pd.concat([existentes, pd.DataFrame([_normalizar_auditoria(auditoria)])], ignore_index=True)
        _escribir_auditorias(existentes)
    logger.info(f"Auditoría {auditoria.get('auditoria_id')} guardada")


def eliminar_auditoria(contrato_id: str) -> None:
    if not AUDITORIAS_CSV.exists():
        return
    df = leer_auditorias()
    df = df[df["contrato_id"].astype(str) != str(contrato_id)]
    _escribir_auditorias(df)


def guardar_reporte_comparativo(filas: list[dict]) -> str:
    df = pd.DataFrame(filas)
    df.to_csv(LOTE_COMPARATIVO_CSV, index=False)
    return str(LOTE_COMPARATIVO_CSV)


def _normalizar_auditoria(auditoria: dict) -> dict:
    base = {col: pd.NA for col in _COLUMNAS_AUDITORIA}
    for col in _COLUMNAS_AUDITORIA:
        if col in auditoria:
            base[col] = auditoria[col]
    return base


def _leer_auditorias_normalizadas() -> list[dict]:
    filas: list[dict] = []
    with open(AUDITORIAS_CSV, encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        next(reader, None)  # descartar encabezado historico, aunque sea incompleto
        for row in reader:
            row = [cell.strip() for cell in row]
            if not row or all(cell == "" for cell in row):
                continue
            filas.append(_mapear_fila_auditoria(row))
    return filas


def _mapear_fila_auditoria(row: list[str]) -> dict:
    base = {col: pd.NA for col in _COLUMNAS_AUDITORIA}
    if len(row) >= 1:
        base["auditoria_id"] = row[0]
    if len(row) >= 2:
        base["contrato_id"] = row[1]
    if len(row) >= 3:
        base["fecha"] = row[2]
    if len(row) >= 4:
        base["total_clausulas"] = row[3]
    if len(row) >= 5:
        base["clausulas_riesgo"] = row[4]
    if len(row) >= 6:
        base["resultado"] = row[5]
    if len(row) >= 7:
        base["score"] = row[6]
    if len(row) >= 8:
        base["nivel_riesgo"] = row[7]
    if len(row) >= 9:
        base["nombre"] = row[8]
    if len(row) >= 10:
        base["categoria"] = row[9]
    if len(row) >= 11:
        base["motor_riesgo"] = row[10]
    if len(row) >= 12:
        base["fuente_tokenizacion"] = row[11]
    return base


def _escribir_auditorias(df: pd.DataFrame) -> None:
    df = df.copy()
    for col in _COLUMNAS_AUDITORIA:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[_COLUMNAS_AUDITORIA]
    df.to_csv(AUDITORIAS_CSV, index=False)
