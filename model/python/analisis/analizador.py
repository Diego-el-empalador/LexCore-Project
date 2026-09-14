"""Funciones analiticas de apoyo para LexCore.

Autor: GPT-5.4
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from controller.utils.config import DATASET_CONTRATOS


def cargar_dataset_referencia() -> dict[str, Any]:
    """Carga el dataset de referencia y resume sus metricas globales."""
    if not DATASET_CONTRATOS.exists():
        return {
            "dataframe": pd.DataFrame(),
            "total_registros": 0,
            "porcentaje_abusivas": 0.0,
            "tipos_contrato": {},
            "tipos_clausula": {},
            "severidades": {},
            "top_riesgos": {},
            "score_promedio_dataset": 100.0,
        }

    df = pd.read_csv(DATASET_CONTRATOS)
    df["es_abusiva"] = df["es_abusiva"].astype(int)
    severidad_score = {"bajo": 5, "medio": 15, "alto": 30, "critico": 45}
    score_promedio = 100.0 - float(
        df["severidad"].map(severidad_score).fillna(10).mean()
    )
    return {
        "dataframe": df,
        "total_registros": int(len(df)),
        "porcentaje_abusivas": round(float(df["es_abusiva"].mean() * 100), 2),
        "tipos_contrato": df["tipo_contrato"].value_counts().to_dict(),
        "tipos_clausula": df["tipo_clausula"].value_counts().to_dict(),
        "severidades": df["severidad"].value_counts().to_dict(),
        "top_riesgos": df[df["es_abusiva"] == 1]["tipo_clausula"].value_counts().head(5).to_dict(),
        "score_promedio_dataset": round(max(score_promedio, 0.0), 2),
    }


def calcular_perfil_estadistico(clausulas: list[dict[str, Any]]) -> dict[str, Any]:
    if not clausulas:
        return {
            "total_clausulas": 0,
            "clausulas_riesgo": 0,
            "porcentaje_riesgo": 0.0,
            "riesgo_promedio": 0.0,
            "riesgo_desviacion": 0.0,
            "riesgo_maximo": 0,
            "longitud_promedio": 0.0,
            "tipos_clausula": {},
            "severidades": {},
            "fecha_calculo": datetime.now().isoformat(),
        }

    df = pd.DataFrame(clausulas)
    tipos = df["tipo"].value_counts().to_dict() if "tipo" in df.columns else {}
    severidades = df["severidad"].value_counts().to_dict() if "severidad" in df.columns else {}

    pesos = np.array([c.get("peso_riesgo", 1) for c in clausulas], dtype=float)
    longitudes = np.array([len(str(c.get("texto", ""))) for c in clausulas], dtype=float)
    clausulas_riesgo = sum(1 for c in clausulas if c.get("es_riesgosa", False))
    total = len(clausulas)

    return {
        "total_clausulas": total,
        "clausulas_riesgo": clausulas_riesgo,
        "porcentaje_riesgo": round((clausulas_riesgo / total) * 100, 2) if total else 0.0,
        "riesgo_promedio": round(float(np.mean(pesos)), 2),
        "riesgo_desviacion": round(float(np.std(pesos)), 2),
        "riesgo_maximo": int(np.max(pesos)),
        "longitud_promedio": round(float(np.mean(longitudes)), 2),
        "tipos_clausula": tipos,
        "severidades": severidades,
        "fecha_calculo": datetime.now().isoformat(),
    }


def detectar_anomalias(clausulas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identifica clausulas atipicas por longitud y peso de riesgo."""
    if len(clausulas) < 3:
        return []

    longitudes = np.array([len(str(c.get("texto", ""))) for c in clausulas], dtype=float)
    pesos = np.array([float(c.get("peso_riesgo", 1)) for c in clausulas], dtype=float)

    long_std = np.std(longitudes) or 1.0
    peso_std = np.std(pesos) or 1.0
    long_z = (longitudes - np.mean(longitudes)) / long_std
    peso_z = (pesos - np.mean(pesos)) / peso_std

    anomalias: list[dict[str, Any]] = []
    for idx, clausula in enumerate(clausulas):
        if abs(long_z[idx]) >= 2 or abs(peso_z[idx]) >= 1.5:
            anomalias.append(
                {
                    "id": clausula.get("id"),
                    "tipo": clausula.get("tipo"),
                    "motivo": "longitud_atipica" if abs(long_z[idx]) >= 2 else "riesgo_atipico",
                    "score_z": round(float(max(abs(long_z[idx]), abs(peso_z[idx]))), 2),
                    "texto": clausula.get("texto", ""),
                }
            )
    return anomalias


def generar_resumen_ejecutivo(dictamen: dict[str, Any]) -> str:
    """Genera un resumen ejecutivo en lenguaje natural."""
    nombre = dictamen.get("nombre", "Contrato")
    score = dictamen.get("score", 0)
    nivel = dictamen.get("nivel_riesgo", "DESCONOCIDO")
    total = dictamen.get("total_clausulas", 0)
    riesgosas = dictamen.get("clausulas_riesgosas", 0)
    recomendacion = dictamen.get("recomendacion_final", "")
    return (
        f"El contrato '{nombre}' fue evaluado con un score de seguridad de {score}/100 y "
        f"un nivel de riesgo {nivel}. Se revisaron {total} clausulas, de las cuales "
        f"{riesgosas} presentan observaciones relevantes. {recomendacion}"
    )


def generar_dataframe_clausulas(clausulas: list[dict[str, Any]]) -> pd.DataFrame:
    if not clausulas:
        return pd.DataFrame()

    df = pd.DataFrame(clausulas)
    columnas_rename = {
        "id": "ID",
        "tipo": "Tipo",
        "texto": "Texto",
        "severidad": "Severidad",
        "es_riesgosa": "Es Riesgosa",
        "peso_riesgo": "Peso de Riesgo",
        "categoria": "Categoria",
        "articulo_referencia": "Articulo de Referencia",
        "recomendacion": "Recomendacion",
        "explicacion": "Explicacion",
    }
    df = df.rename(columns={k: v for k, v in columnas_rename.items() if k in df.columns})
    if "Es Riesgosa" in df.columns:
        df["Es Riesgosa"] = df["Es Riesgosa"].map({True: "Si", False: "No"})
    return df


def comparar_con_promedio(estadisticas_actual: dict[str, Any], historial: list[dict[str, Any]]) -> dict[str, Any]:
    if not historial:
        return {"promedio_historico": None, "diferencia": None, "tendencia": "sin_historial"}

    porcentajes = np.array([float(h.get("porcentaje_riesgo", 0)) for h in historial], dtype=float)
    promedio_historico = float(np.mean(porcentajes))
    actual = float(estadisticas_actual.get("porcentaje_riesgo", 0))
    diferencia = round(actual - promedio_historico, 2)
    if diferencia < -2:
        tendencia = "mejor"
    elif diferencia > 2:
        tendencia = "peor"
    else:
        tendencia = "igual"
    return {
        "promedio_historico": round(promedio_historico, 2),
        "diferencia": diferencia,
        "tendencia": tendencia,
    }
