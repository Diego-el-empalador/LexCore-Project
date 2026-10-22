"""Pipeline principal de LexCore con fallbacks y analisis por lote.

Autor: GPT-5.4
"""

from __future__ import annotations

import re
import time
import uuid
from collections import Counter
from datetime import datetime
from typing import Any, Callable

import pandas as pd

from controller.almacenamiento.lector_csv import (
    guardar_auditoria,
    guardar_hallazgos,
    guardar_reporte_comparativo,
    leer_auditorias,
)
from controller.almacenamiento.lector_json import guardar_contrato_procesado, guardar_contrato_raw
from controller.analisis.estadisticas import calcular_estadisticas
from controller.orquestador.prolog_bridge import (
    detectar_riesgos_por_palabras_clave,
    validar_clausulas,
)
from controller.orquestador.scala_bridge import tokenizar_contrato
from controller.utils.logger import get_logger
from model.python.analisis.analizador import (
    calcular_perfil_estadistico,
    cargar_dataset_referencia,
    detectar_anomalias,
    generar_resumen_ejecutivo,
)
from model.python.modelos.contrato import Contrato, Dictamen

logger = get_logger(__name__)
ProgressCallback = Callable[[str, float], None]
_CABECERAS_ORDINALES = (
    r"primera|segunda|tercera|cuarta|quinta|sexta|septima|séptima|octava|novena|d[eé]cima|"
    r"und[eé]cima|duod[eé]cima|decimotercera|decimocuarta|decimoquinta"
)
_PATRON_CABECERA = re.compile(
    r"(?im)(?=^\s*(?:"
    r"cl[áa]usula|art[íi]culo|secci[óo]n|cap[íi]tulo|anexo|numeral|literal|condici[óo]n|"
    + _CABECERAS_ORDINALES
    + r"|"
    r"[ivxlcdm]+[\.\)\-:]|\d+[\.\)\-:]|[a-z][\.\)]"
    r"))"
)
_PATRON_CABECERA_LINEA = re.compile(
    r"(?im)^\s*(?:cl[áa]usula|art[íi]culo|secci[óo]n|cap[íi]tulo|anexo|numeral|literal|condici[óo]n|"
    + _CABECERAS_ORDINALES
    + r"|[ivxlcdm]+[\.\)\-:]|\d+[\.\)\-:]|[a-z][\.\)])"
)


def _notificar(callback: ProgressCallback | None, mensaje: str, progreso: float) -> None:
    if callback is not None:
        callback(mensaje, progreso)


def _chunk_texto_largo(texto: str, max_chars: int = 10_000) -> list[str]:
    if len(texto) <= max_chars:
        return [texto]

    bloques = _PATRON_CABECERA.split(texto)
    chunks: list[str] = []
    actual = ""
    for bloque in bloques:
        bloque = bloque.strip()
        if not bloque:
            continue
        if len(actual) + len(bloque) + 2 <= max_chars:
            actual = f"{actual}\n{bloque}".strip()
        else:
            if actual:
                chunks.append(actual)
            if len(bloque) <= max_chars:
                actual = bloque
            else:
                for i in range(0, len(bloque), max_chars):
                    chunks.append(bloque[i : i + max_chars])
                actual = ""
    if actual:
        chunks.append(actual)
    return chunks or [texto]


def _contar_marcadores_clausula(texto: str) -> int:
    return len(re.findall(_PATRON_CABECERA.pattern, texto))


def _segmentar_clausulas_python(texto: str) -> list[str]:
    texto = texto.strip()
    if not texto:
        return []

    texto = re.sub(r"(?i)(?:p[aá]gina)\s+\d+\s+de\s+\d+", "\n", texto)
    texto = re.sub(
        r"(?i)(?<=[\.\:;])\s+(?=(?:"
        + _CABECERAS_ORDINALES
        + r")\s*:)",
        "\n",
        texto,
    )
    texto = re.sub(
        r"(?i)(?<=[\.\:;])\s+(?=(?:cl[áa]usula|art[íi]culo|secci[óo]n|cap[íi]tulo|anexo|numeral|literal|condici[óo]n)\b)",
        "\n",
        texto,
    )

    segmentos = [parte.strip() for parte in _PATRON_CABECERA.split(texto) if parte and parte.strip()]
    if len(segmentos) > 1:
        return _refinar_segmentos(segmentos)

    segmentos = [
        parte.strip()
        for parte in re.split(
            r"\n{2,}|(?<=\.)\s+(?=(?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SEPTIMA|SÉPTIMA|OCTAVA|NOVENA|DECIMA|DÉCIMA)\b)",
            texto,
            flags=re.IGNORECASE,
        )
        if parte.strip()
    ]
    return _refinar_segmentos(segmentos)


def _refinar_segmentos(segmentos: list[str]) -> list[str]:
    refinados: list[str] = []
    for idx, segmento in enumerate(segmentos):
        limpio = re.sub(r"\s+", " ", segmento).strip()
        if not limpio:
            continue
        if idx == 0 and len(segmentos) > 1 and not _PATRON_CABECERA_LINEA.search(limpio):
            # El bloque previo a "PRIMERA/CLAUSULA I" suele ser solo encabezado del contrato.
            continue
        if len(limpio) > 900 and ";" in limpio:
            subpartes = [s.strip() for s in re.split(r";\s+(?=(?:el|la|las|los|si|en caso|para|cualquier|ninguna parte))", limpio, flags=re.IGNORECASE) if s.strip()]
            if len(subpartes) > 1:
                refinados.extend(subpartes)
                continue
        refinados.append(limpio)
    return refinados


def _detectar_tipo_basico(texto: str) -> str:
    lower = texto.lower()
    reglas = {
        "no_competencia": ["no competencia", "competidor", "exclusividad"],
        "propiedad_intelectual": ["propiedad intelectual", "codigo fuente", "marca", "licencia"],
        "datos_personales": ["datos personales", "consentimiento", "privacidad", "biometric"],
        "arbitraje": ["arbitraje", "laudo", "tribunal arbitral"],
        "modificacion_unilateral": ["unilateral", "sola discrecion", "sin acuerdo"],
        "penalidad": ["multa", "penalidad", "sancion", "incumplimiento", "descuento", "retencion", "hasta el cincuenta por ciento", "50%"],
        "plazo": ["plazo", "dias", "meses", "fecha", "vencimiento", "dias habiles", "ciento veinte", "120"],
        "confidencialidad": ["confidencial", "reserva", "divulgar"],
        "rescision": ["resolver", "rescindir", "terminar", "preaviso"],
        "obligacion": ["debe", "obligado", "cumplir", "pagar", "honorarios", "sin costo adicional", "iteraciones sucesivas", "remuneracion"],
    }
    for tipo, palabras in reglas.items():
        if any(palabra in lower for palabra in palabras):
            return tipo
    return "general"


def _tokenizar_basico_python(texto: str, contrato_id: str, nombre: str) -> dict[str, Any]:
    segmentos = _segmentar_clausulas_python(texto)
    if not segmentos:
        segmentos = [seg.strip() for seg in re.split(r"\n{2,}", texto) if seg.strip()] or [texto.strip()]

    clausulas = []
    for idx, segmento in enumerate(segmentos, start=1):
        clausulas.append(
            {
                "id": idx,
                "tipo": _detectar_tipo_basico(segmento),
                "texto": segmento,
                "partes": [p.strip() for p in re.split(r"[;,\n]+", segmento) if p.strip()],
                "riesgo_inicial": min(10, max(0, len(segmento.split()) // 18)),
            }
        )
    return {
        "contrato_id": contrato_id,
        "nombre": nombre,
        "riesgo_inicial": round(sum(c["riesgo_inicial"] for c in clausulas) / max(len(clausulas), 1), 2),
        "clausulas": clausulas,
        "fuente_tokenizacion": "python_fallback",
    }


def _limpiar_clausulas_tokenizadas(clausulas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(clausulas) <= 1:
        return clausulas
    primera = clausulas[0]
    segunda = clausulas[1]
    texto_primera = str(primera.get("texto", "")).strip()
    texto_segunda = str(segunda.get("texto", "")).strip()
    if (
        primera.get("tipo") == "general"
        and not _PATRON_CABECERA_LINEA.search(texto_primera)
        and _PATRON_CABECERA_LINEA.search(texto_segunda)
    ):
        clausulas = clausulas[1:]
    for idx, clausula in enumerate(clausulas, start=1):
        clausula["id"] = idx
    return clausulas


def _tokenizar_con_fallback(texto: str, contrato_id: str, nombre: str) -> tuple[dict[str, Any], str]:
    chunks = _chunk_texto_largo(texto)
    clausulas: list[dict[str, Any]] = []
    fuente = "scala"
    for idx, chunk in enumerate(chunks, start=1):
        resultado_python = _tokenizar_basico_python(chunk, f"{contrato_id}_{idx}", f"{nombre} - parte {idx}")
        try:
            resultado = tokenizar_contrato(chunk, f"{contrato_id}_{idx}", f"{nombre} - parte {idx}")
            scala_n = len(resultado.get("clausulas", []))
            python_n = len(resultado_python.get("clausulas", []))
            if len(resultado.get("clausulas", [])) <= 1 and _contar_marcadores_clausula(chunk) > 1:
                raise RuntimeError("Scala no separó las cláusulas esperadas; se activa fallback Python.")
            if python_n >= scala_n + 2 and python_n >= 3:
                logger.warning(
                    "Python detectó mejor segmentación que Scala en chunk %s: scala=%s python=%s",
                    idx,
                    scala_n,
                    python_n,
                )
                resultado = resultado_python
                fuente = "mixto_python_scala" if fuente == "scala" else fuente
        except Exception as exc:
            logger.exception("Scala fallo en chunk %s, se usara fallback Python: %s", idx, exc)
            resultado = resultado_python
            fuente = "mixto_python_scala" if fuente == "scala" else fuente
        for clausula in resultado.get("clausulas", []):
            nueva = dict(clausula)
            nueva["id"] = len(clausulas) + 1
            clausulas.append(nueva)
    return {
        "contrato_id": contrato_id,
        "nombre": nombre,
        "riesgo_inicial": round(sum(c.get("riesgo_inicial", 0) for c in clausulas) / max(len(clausulas), 1), 2),
        "clausulas": _limpiar_clausulas_tokenizadas(clausulas),
        "fuente_tokenizacion": fuente,
        "chunks_procesados": len(chunks),
    }, fuente


def _comparar_con_dataset(categoria: str, score_actual: int, clausulas: list[dict[str, Any]]) -> dict[str, Any]:
    dataset = cargar_dataset_referencia()
    df = dataset["dataframe"]
    if df.empty:
        return {
            "score_promedio_dataset": None,
            "diferencia_score": None,
            "tipo_mas_frecuente": None,
            "frecuencias_palabras": {},
        }

    filtrado = df[df["tipo_contrato"] == categoria] if categoria in set(df["tipo_contrato"]) else df
    score_promedio = dataset["score_promedio_dataset"]
    palabras = Counter()
    for texto in filtrado["texto_clausula"].astype(str):
        for palabra in re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}", texto.lower()):
            if palabra not in {"clausula", "contrato", "parte", "partes", "entre"}:
                palabras[palabra] += 1

    tipos_actuales = Counter(str(c.get("tipo", "general")) for c in clausulas)
    return {
        "score_promedio_dataset": score_promedio,
        "diferencia_score": round(float(score_actual) - float(score_promedio), 2),
        "tipo_mas_frecuente": tipos_actuales.most_common(1)[0][0] if tipos_actuales else None,
        "frecuencias_palabras": dict(palabras.most_common(10)),
    }


def analizar_contrato(
    texto: str,
    nombre: str,
    categoria: str = "general",
    progreso_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    if not isinstance(texto, str):
        raise TypeError("El contenido del contrato debe ser texto.")

    if not isinstance(nombre, str):
        raise TypeError("El nombre del contrato debe ser texto.")

    texto = texto.strip()

    if not texto:
        raise ValueError("El contrato no puede estar vacío.")

    if len(texto) < 50:
        raise ValueError(
            "El contrato contiene muy poco texto para realizar un análisis confiable."
        )

    nombre = nombre.strip()

    if not nombre:
        raise ValueError("El nombre del contrato no puede estar vacío.")

    if len(nombre) < 3:
        raise ValueError(
            "El nombre del contrato debe contener al menos 3 caracteres."
        )

    contrato_id = str(uuid.uuid4())[:8]
    logger.info(f"Iniciando análisis del contrato '{nombre}' [{contrato_id}] categoria={categoria}")

    try:
        guardar_contrato_raw(
            {
                "contrato_id": contrato_id,
                "nombre": nombre,
                "categoria": categoria,
                "texto": texto,
                "fecha": datetime.now().isoformat(),
            }
        )
    except Exception as exc:
        logger.exception(
            "Error al guardar el contrato '%s' [%s]: %s",
            nombre,
            contrato_id,
            exc,
        )
        raise RuntimeError(
            "No se pudo guardar el contrato antes de iniciar el análisis."
        ) from exc


    timings: dict[str, float] = {}
    _notificar(progreso_callback, "Procesando con Scala...", 0.15)
    t0 = time.perf_counter()
    scala_output, fuente_tokenizacion = _tokenizar_con_fallback(texto, contrato_id, nombre)
    timings["tokenizacion"] = round(time.perf_counter() - t0, 3)

    _notificar(progreso_callback, "Razonando con Prolog...", 0.5)
    t1 = time.perf_counter()
    try:
        hallazgos = validar_clausulas(scala_output["clausulas"], categoria=categoria)
        motor_riesgo = "prolog"
    except Exception as exc:
        logger.exception("Prolog fallo, se usara fallback por palabras clave: %s", exc)
        hallazgos = detectar_riesgos_por_palabras_clave(scala_output["clausulas"])
        motor_riesgo = "python_keyword_fallback"
    timings["prolog"] = round(time.perf_counter() - t1, 3)

    _notificar(progreso_callback, "Calculando estadísticas...", 0.8)
    t2 = time.perf_counter()
    estadisticas = calcular_estadisticas(scala_output["clausulas"], hallazgos)

    contrato_obj = Contrato(
        contrato_id=contrato_id,
        nombre=nombre,
        categoria=categoria,
        texto_original=texto,
    )
    contrato_obj.cargar_desde_scala(scala_output, hallazgos)
    clausulas_evaluadas = [clausula.to_json() for clausula in contrato_obj.clausulas]
    perfil = calcular_perfil_estadistico(clausulas_evaluadas)
    dictamen = Dictamen(contrato=contrato_obj, estadisticas=perfil)
    resumen_dictamen = dictamen.resumen()
    resumen_texto = generar_resumen_ejecutivo(resumen_dictamen)
    anomalias = detectar_anomalias(clausulas_evaluadas)
    comparacion_dataset = _comparar_con_dataset(categoria, resumen_dictamen["score"], clausulas_evaluadas)
    timings["estadisticas"] = round(time.perf_counter() - t2, 3)

    resultado = {
        "contrato_id": contrato_id,
        "nombre": nombre,
        "categoria": categoria,
        "clausulas": clausulas_evaluadas,
        "hallazgos": hallazgos,
        "estadisticas": estadisticas,
        "perfil": perfil,
        "score": resumen_dictamen["score"],
        "nivel_riesgo": resumen_dictamen["nivel_riesgo"],
        "recomendacion_final": resumen_dictamen["recomendacion_final"],
        "resumen_ejecutivo": resumen_texto,
        "anomalias": anomalias,
        "comparacion_dataset": comparacion_dataset,
        "fuente_tokenizacion": fuente_tokenizacion,
        "motor_riesgo": motor_riesgo,
        "timings": timings,
        "fecha_analisis": datetime.now().isoformat(),
        "total_clausulas": len(clausulas_evaluadas),
        "clausulas_riesgosas": len([c for c in clausulas_evaluadas if c.get("es_riesgosa")]),
    }

    try:
        guardar_contrato_procesado(resultado)
        guardar_hallazgos(contrato_id, hallazgos)
        guardar_auditoria(
            {
                "auditoria_id": str(uuid.uuid4())[:8],
                "contrato_id": contrato_id,
                "fecha": resultado["fecha_analisis"],
                "total_clausulas": len(clausulas_evaluadas),
                "clausulas_riesgo": len(hallazgos),
                "resultado": "con_riesgos" if hallazgos else "aprobado",
                "score": resumen_dictamen["score"],
                "nivel_riesgo": resumen_dictamen["nivel_riesgo"],
                "nombre": nombre,
                "categoria": categoria,
                "motor_riesgo": motor_riesgo,
                "fuente_tokenizacion": fuente_tokenizacion,
            }
        )
    except Exception as exc:
        logger.exception(
            "Error al guardar los resultados del contrato '%s' [%s]: %s",
            nombre,
            contrato_id,
            exc,
        )
        raise RuntimeError(
            "El análisis terminó, pero no se pudieron guardar sus resultados."
        ) from exc

    _notificar(progreso_callback, "Análisis completado.", 1.0)
    return resultado

def analizar_lote(
    archivos: list[dict[str, Any]],
    categoria: str = "general",
    progreso_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    resultados: list[dict[str, Any]] = []
    comparativo: list[dict[str, Any]] = []
    total = max(len(archivos), 1)

    for idx, archivo in enumerate(archivos, start=1):
        nombre = str(archivo.get("nombre", f"Contrato {idx}"))
        texto = str(archivo.get("texto", ""))
        base = ((idx - 1) / total) * 0.9

        def callback_local(mensaje: str, progreso: float) -> None:
            _notificar(
                progreso_callback,
                f"[{idx}/{total}] {nombre}: {mensaje}",
                min(0.95, base + (progreso * 0.9 / total)),
            )

        resultado = analizar_contrato(texto, nombre, categoria=categoria, progreso_callback=callback_local)
        resultados.append(resultado)
        comparativo.append(
            {
                "contrato_id": resultado["contrato_id"],
                "nombre": resultado["nombre"],
                "categoria": resultado["categoria"],
                "score": resultado["score"],
                "nivel_riesgo": resultado["nivel_riesgo"],
                "total_clausulas": resultado["total_clausulas"],
                "clausulas_riesgosas": resultado["clausulas_riesgosas"],
                "fuente_tokenizacion": resultado["fuente_tokenizacion"],
                "motor_riesgo": resultado["motor_riesgo"],
            }
        )

    csv_path = guardar_reporte_comparativo(comparativo)
    auditorias = leer_auditorias()
    promedio_lote = 0.0
    if not auditorias.empty and "score" in auditorias:
        scores = pd.to_numeric(auditorias["score"], errors="coerce").dropna()
        promedio_lote = round(float(scores.mean()), 2) if not scores.empty else 0.0
    _notificar(progreso_callback, "Reporte comparativo listo.", 1.0)
    return {
        "resultados": resultados,
        "comparativo": comparativo,
        "csv_path": csv_path,
        "resumen": {
            "total_archivos": len(resultados),
            "score_promedio_lote": round(sum(r["score"] for r in resultados) / max(len(resultados), 1), 2),
            "score_promedio_historico": promedio_lote,
        },
    }
