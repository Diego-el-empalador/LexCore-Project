"""Generacion de reportes JSON, texto y comparativos.

Autor: GPT-5.4
"""

from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from controller.utils.logger import get_logger

logger = get_logger(__name__)


def generar_reporte(resultado: dict) -> str:
    reporte = {
        "generado_en": datetime.now().isoformat(),
        "contrato_id": resultado.get("contrato_id"),
        "nombre": resultado.get("nombre"),
        "categoria": resultado.get("categoria"),
        "score": resultado.get("score"),
        "nivel_riesgo": resultado.get("nivel_riesgo"),
        "resumen_ejecutivo": resultado.get("resumen_ejecutivo"),
        "resumen": resultado.get("estadisticas"),
        "comparacion_dataset": resultado.get("comparacion_dataset"),
        "anomalias": resultado.get("anomalias"),
        "hallazgos": resultado.get("hallazgos"),
        "clausulas": resultado.get("clausulas"),
    }
    logger.info(f"Reporte generado para contrato {resultado.get('contrato_id')}")
    return json.dumps(reporte, ensure_ascii=False, indent=2)


def generar_reporte_texto(resultado: dict) -> str:
    hallazgos = resultado.get("hallazgos", [])
    bloques = [
        f"Reporte LexCore - {resultado.get('nombre')}",
        f"Contrato ID: {resultado.get('contrato_id')}",
        f"Categoria: {resultado.get('categoria')}",
        f"Score: {resultado.get('score')} / 100",
        f"Nivel de riesgo: {resultado.get('nivel_riesgo')}",
        "",
        resultado.get("resumen_ejecutivo", ""),
        "",
        "Hallazgos principales:",
    ]
    if hallazgos:
        for hallazgo in hallazgos:
            bloques.append(
                f"- Clausula {hallazgo.get('clausula_id')}: {hallazgo.get('tipo_riesgo')} "
                f"({hallazgo.get('severidad')}) | {hallazgo.get('articulo_violado')} | "
                f"{hallazgo.get('descripcion_riesgo')}"
            )
    else:
        bloques.append("- No se detectaron hallazgos de riesgo relevantes.")
    return "\n".join(bloques)


def generar_reporte_comparativo_csv(resultados: list[dict]) -> str:
    df = pd.DataFrame(
        [
            {
                "contrato_id": r.get("contrato_id"),
                "nombre": r.get("nombre"),
                "categoria": r.get("categoria"),
                "score": r.get("score"),
                "nivel_riesgo": r.get("nivel_riesgo"),
                "total_clausulas": r.get("total_clausulas"),
                "clausulas_riesgosas": r.get("clausulas_riesgosas"),
                "motor_riesgo": r.get("motor_riesgo"),
                "fuente_tokenizacion": r.get("fuente_tokenizacion"),
            }
            for r in resultados
        ]
    )
    return df.to_csv(index=False)
