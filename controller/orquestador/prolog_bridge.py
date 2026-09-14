"""Puente entre Python y SWI-Prolog para deteccion de riesgos.

Autor: GPT-5.4
"""

from __future__ import annotations

from typing import Any

from controller.utils.config import PROLOG_DIR
from controller.utils.logger import get_logger

try:
    from pyswip import Prolog
except Exception:  # pragma: no cover - depende del sistema local
    Prolog = None

logger = get_logger(__name__)

_DEFAULT_ARTICULOS = {
    "penalidad": ("Art. 1346 CC", "Penalidad excesiva reducible por el juez."),
    "plazo": ("Art. 1238 CC", "El plazo debe ser determinado o determinable."),
    "jornada": ("Art. 25 Constitucion", "No es valido imponer disponibilidad permanente o jornadas desproporcionadas."),
    "remuneracion_abusiva": ("Art. 24 Constitucion", "La remuneracion debe ser equitativa y suficiente; no pueden imponerse descuentos o esperas desproporcionadas."),
    "rescision": ("Art. 1371 CC", "La resolucion requiere causal y comunicacion valida."),
    "confidencialidad": ("Art. 1362 CC", "Las obligaciones deben ejecutarse con buena fe."),
    "no_competencia": ("Art. 1400 CC", "Una restriccion excesiva puede ser abusiva."),
    "propiedad_intelectual": ("Dec. Leg. 822", "La cesion de derechos debe ser clara y proporcionada."),
    "datos_personales": ("Ley 29733", "El tratamiento de datos necesita base legal y finalidad."),
    "arbitraje": ("D. Leg. 1071", "El arbitraje debe respetar equilibrio y consentimiento informado."),
    "modificacion_unilateral": ("Art. 1354 CC", "No se admiten cambios unilaterales abusivos."),
    "general": ("Art. 1400 CC", "No deben existir clausulas que generen desequilibrio importante."),
}

_PALABRAS_CLAVE = {
    "no_competencia": [("sin compensacion", "alto"), ("todo el pais", "alto"), ("diez anos", "critico"), ("exclusividad absoluta", "critico")],
    "propiedad_intelectual": [("codigo fuente", "alto"), ("sin pago adicional", "alto"), ("pasara automaticamente", "critico"), ("irrevocable", "critico"), ("perpetua", "critico")],
    "datos_personales": [("sin consentimiento", "critico"), ("datos biometric", "critico"), ("publicar la deuda", "alto")],
    "arbitraje": [("arbitraje obligatorio", "alto"), ("solo por arbitraje privado", "critico"), ("renuncia a la via judicial", "critico"), ("renuncian de forma expresa a los fueros", "critico"), ("elegidas por el cliente", "critico")],
    "modificacion_unilateral": [("modificar unilateralmente", "alto"), ("a su sola discrecion", "critico"), ("sin acuerdo del proveedor", "critico")],
    "jornada": [("24 horas", "critico"), ("veinticuatro (24) horas", "critico"), ("7 dias", "critico"), ("siete (7) dias", "critico")],
    "penalidad": [("interes compuesto", "critico"), ("80%", "critico"), ("sin tope", "alto"), ("mantendra indemne", "alto"), ("penalidad resarcitoria", "alto")],
    "rescision": [("sin expresion de causa", "critico"), ("con efecto inmediato", "critico"), ("sin necesidad de justificacion", "critico")],
    "remuneracion_abusiva": [("120 dias", "alto"), ("ciento veinte", "alto"), ("50%", "critico"), ("retenciones de hasta", "critico"), ("sin costo adicional", "critico")],
    "general": [("sin responsabilidad alguna", "critico"), ("renuncia a reclamar", "critico")],
}


def _decode(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value)


def _enriquecer_hallazgo(clausula_id: int, tipo_riesgo: str, severidad: str) -> dict[str, Any]:
    articulo, descripcion = _DEFAULT_ARTICULOS.get(tipo_riesgo, _DEFAULT_ARTICULOS["general"])
    return {
        "clausula_id": int(clausula_id),
        "tipo_riesgo": tipo_riesgo,
        "severidad": severidad,
        "articulo_violado": articulo,
        "descripcion_riesgo": descripcion,
    }


def _texto_clausula(clausulas: list[dict], clausula_id: int) -> str:
    for clausula in clausulas:
        if int(clausula.get("id", 0)) == int(clausula_id):
            return str(clausula.get("texto", ""))
    return ""


def _es_hallazgo_preciso(hallazgo: dict[str, Any], texto: str) -> bool:
    lower = texto.lower()
    tipo = str(hallazgo.get("tipo_riesgo", "general"))
    severidad = str(hallazgo.get("severidad", "medio"))
    patrones = {
        "penalidad": ["interes compuesto", "50%", "60%", "70%", "80%", "90%", "100%", "sin tope", "sin limite", "mantendra indemne", "penalidad resarcitoria", "compensar dicho monto", "saldos pendientes de pago"],
        "jornada": ["24 horas", "veinticuatro (24) horas", "7 dias", "siete (7) dias", "respuesta prioritaria", "seis (6) horas"],
        "remuneracion_abusiva": ["120 dias", "ciento veinte", "dias habiles", "50%", "retencion", "descuento", "sin costo adicional", "iteraciones sucesivas"],
        "rescision": ["sin preaviso", "sin expresar causa", "sin notificacion", "sin aviso previo", "sin expresion de causa", "con efecto inmediato", "sin necesidad de justificacion"],
        "no_competencia": ["sin compensacion", "todo el pais", "cinco anos", "diez anos", "exclusividad absoluta", "prohibido prestar servicios", "terceras personas"],
        "propiedad_intelectual": ["codigo fuente", "pasara automaticamente", "sin pago adicional", "irrevocable y exclusiva", "irrevocable", "perpetua", "mundial", "sin regalias"],
        "datos_personales": ["sin consentimiento", "datos biometric", "terceros", "redes sociales"],
        "arbitraje": ["obligatorio", "renuncia a la via judicial", "solo por arbitraje privado", "designado por el vendedor", "renuncian de forma expresa a los fueros", "elegidas por el cliente", "costos legales", "sufragar la totalidad"],
        "modificacion_unilateral": ["modificar unilateralmente", "variar unilateralmente", "a su sola discrecion", "sin acuerdo"],
        "general": ["sin responsabilidad alguna", "renuncia a reclamar", "renuncia a acciones", "no podra cuestionar"],
    }
    hits = sum(1 for patron in patrones.get(tipo, []) if patron in lower)
    if tipo == "remuneracion_abusiva":
        return hits >= 2 or (
            ("sin costo adicional" in lower or "sin compensacion adicional" in lower)
            and ("descuento" in lower or "retencion" in lower or "120 dias" in lower or "ciento veinte" in lower)
        )
    if tipo == "general":
        return hits >= 1
    if severidad == "critico":
        return hits >= 1
    return hits >= 1


def validar_clausulas(clausulas: list[dict], categoria: str = "general") -> list[dict[str, Any]]:
    if Prolog is None:
        raise RuntimeError("pyswip no esta disponible en este entorno.")

    prolog = Prolog()
    for archivo in [
        PROLOG_DIR / "base_conocimiento" / "hechos.pl",
        PROLOG_DIR / "base_conocimiento" / "reglas_generales.pl",
        PROLOG_DIR / "base_conocimiento" / "reglas_civiles.pl",
        PROLOG_DIR / "base_conocimiento" / "reglas_comerciales.pl",
        PROLOG_DIR / "base_conocimiento" / "reglas_laborales.pl",
        PROLOG_DIR / "consultas" / "validar_clausula.pl",
    ]:
        prolog.consult(str(archivo))

    for clausula in clausulas:
        texto_atom = str(clausula.get("texto", "")).replace("\\", "\\\\").replace("'", "\\'")
        tipo = str(clausula.get("tipo", "general")).replace("-", "_")
        prolog.assertz(f"clausula({clausula.get('id', 0)}, {tipo}, '{texto_atom}')")

    hallazgos: list[dict[str, Any]] = []
    soluciones = list(prolog.query("clausula_riesgosa(Id, Tipo, Severidad)"))
    for solucion in soluciones:
        hallazgo = _enriquecer_hallazgo(
            clausula_id=int(solucion["Id"]),
            tipo_riesgo=_decode(solucion["Tipo"]),
            severidad=_decode(solucion["Severidad"]).lower(),
        )
        texto = _texto_clausula(clausulas, hallazgo["clausula_id"])
        if _es_hallazgo_preciso(hallazgo, texto):
            hallazgos.append(hallazgo)

    logger.info(f"Prolog encontró {len(hallazgos)} hallazgos")
    return _deduplicar_hallazgos(hallazgos)


def detectar_riesgos_por_palabras_clave(clausulas: list[dict]) -> list[dict[str, Any]]:
    hallazgos: list[dict[str, Any]] = []
    for clausula in clausulas:
        texto = str(clausula.get("texto", "")).lower()
        encontrado = False
        for tipo, reglas in _PALABRAS_CLAVE.items():
            for palabra, severidad in reglas:
                if palabra in texto:
                    hallazgos.append(
                        _enriquecer_hallazgo(
                            clausula_id=int(clausula.get("id", 0)),
                            tipo_riesgo=tipo,
                            severidad=severidad,
                        )
                    )
                    encontrado = True
                    break
            if encontrado:
                break
    return _deduplicar_hallazgos(hallazgos)


def _deduplicar_hallazgos(hallazgos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    severidad_rank = {"bajo": 1, "medio": 2, "alto": 3, "critico": 4}
    agrupados: dict[tuple[int, str], dict[str, Any]] = {}
    for hallazgo in hallazgos:
        clave = (int(hallazgo["clausula_id"]), str(hallazgo["tipo_riesgo"]))
        previo = agrupados.get(clave)
        if previo is None or severidad_rank.get(hallazgo["severidad"], 0) > severidad_rank.get(previo["severidad"], 0):
            agrupados[clave] = hallazgo
    por_clausula: dict[int, list[dict[str, Any]]] = {}
    for hallazgo in agrupados.values():
        por_clausula.setdefault(int(hallazgo["clausula_id"]), []).append(hallazgo)

    filtrados: list[dict[str, Any]] = []
    for _, lista in por_clausula.items():
        tiene_especifico = any(h["tipo_riesgo"] != "general" for h in lista)
        candidatos = [h for h in lista if h["tipo_riesgo"] != "general"] if tiene_especifico else lista
        candidatos = sorted(
            candidatos,
            key=lambda item: (
                severidad_rank.get(item["severidad"], 0),
                0 if item["tipo_riesgo"] != "general" else 1,
            ),
            reverse=True,
        )
        filtrados.extend(candidatos[:2])

    return sorted(filtrados, key=lambda item: (item["clausula_id"], -severidad_rank.get(item["severidad"], 0), item["tipo_riesgo"]))
