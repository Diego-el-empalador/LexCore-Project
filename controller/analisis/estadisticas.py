"""Calculo de metricas y agregados del analisis.

Autor: GPT-5.4
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from controller.utils.logger import get_logger

logger = get_logger(__name__)


def calcular_estadisticas(clausulas: list[dict], hallazgos: list[dict]) -> dict:
    total = len(clausulas)
    if total == 0:
        return {
            "total": 0,
            "riesgo": 0,
            "porcentaje_riesgo": 0.0,
            "tipos_clausula": {},
            "severidades": {},
            "promedio_tokens": 0,
            "promedio_longitud": 0,
        }

    df_c = pd.DataFrame(clausulas)
    df_h = pd.DataFrame(hallazgos) if hallazgos else pd.DataFrame()

    tipos = df_c["tipo"].value_counts().to_dict() if "tipo" in df_c else {}
    severidades = df_h["severidad"].value_counts().to_dict() if not df_h.empty and "severidad" in df_h else {}
    prom_tokens = int(np.mean([len(str(c.get("texto", "")).split()) for c in clausulas]))
    prom_longitud = int(np.mean([len(str(c.get("texto", ""))) for c in clausulas]))

    logger.info(f"Estadísticas: {total} cláusulas, {len(hallazgos)} con riesgo")
    return {
        "total": total,
        "riesgo": len(hallazgos),
        "porcentaje_riesgo": round(len(hallazgos) / total * 100, 2),
        "tipos_clausula": tipos,
        "severidades": severidades,
        "promedio_tokens": prom_tokens,
        "promedio_longitud": prom_longitud,
    }
