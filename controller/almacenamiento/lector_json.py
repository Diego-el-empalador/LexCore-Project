"""Persistencia JSON de contratos procesados y entradas crudas.

Autor: GPT-5.4
"""

from __future__ import annotations

import json
from typing import Any

from controller.utils.config import CONTRATOS_PROC, CONTRATOS_RAW
from controller.utils.logger import get_logger

logger = get_logger(__name__)


def _leer_json(path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def leer_contratos_raw() -> list[dict[str, Any]]:
    return _leer_json(CONTRATOS_RAW)


def guardar_contrato_raw(contrato: dict[str, Any]) -> None:
    datos = _leer_json(CONTRATOS_RAW)
    datos.append(contrato)
    with open(CONTRATOS_RAW, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=2)


def leer_contratos_procesados() -> list[dict[str, Any]]:
    return _leer_json(CONTRATOS_PROC)


def obtener_contrato_procesado(contrato_id: str) -> dict[str, Any]:
    return next((c for c in leer_contratos_procesados() if c.get("contrato_id") == contrato_id), {})


def guardar_contrato_procesado(contrato: dict[str, Any]) -> None:
    datos = [c for c in leer_contratos_procesados() if c.get("contrato_id") != contrato.get("contrato_id")]
    datos.append(contrato)
    with open(CONTRATOS_PROC, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=2)
    logger.info(f"Contrato {contrato.get('contrato_id')} guardado")


def eliminar_contrato_procesado(contrato_id: str) -> None:
    datos = [c for c in leer_contratos_procesados() if c.get("contrato_id") != contrato_id]
    with open(CONTRATOS_PROC, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=2)
