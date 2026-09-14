"""Modelo de contrato y dictamen final del analisis.

Autor: GPT-5.4
"""

from datetime import datetime
from typing import Any, List

from model.python.modelos.clausula import Clausula, fabricar_clausula


class Contrato:
    _SEVERIDAD_RANK = {"bajo": 1, "medio": 2, "alto": 3, "critico": 4}

    def __init__(self, contrato_id: str, nombre: str, categoria: str, texto_original: str):
        self.contrato_id = contrato_id
        self.nombre = nombre
        self.categoria = categoria
        self.texto_original = texto_original
        self.fecha_analisis = datetime.now().isoformat()
        self.clausulas: List[Clausula] = []

    def agregar_clausula(self, id: str, tipo: str, texto: str, severidad: str, **kwargs: Any) -> Clausula:
        clausula = fabricar_clausula(
            categoria=self.categoria,
            id=id,
            tipo=tipo,
            texto=texto,
            severidad=severidad,
            **kwargs,
        )
        self.clausulas.append(clausula)
        return clausula

    def cargar_desde_scala(self, scala_output: dict, hallazgos_prolog: list) -> None:
        mapa_hallazgos: dict[str, list[dict[str, Any]]] = {}
        for hallazgo in hallazgos_prolog:
            clausula_id = hallazgo.get("clausula_id") or hallazgo.get("id", "")
            if clausula_id == "":
                continue
            mapa_hallazgos.setdefault(str(clausula_id), []).append(hallazgo)

        for cl in scala_output.get("clausulas", []):
            cid = str(cl.get("id", ""))
            hallazgos_clausula = mapa_hallazgos.get(cid, [])
            principal = self._hallazgo_principal(hallazgos_clausula)
            tipo_base = cl.get("tipo", "general")
            tipo_mostrado = principal.get("tipo_riesgo", tipo_base) if principal else tipo_base
            severidad = principal.get("severidad", "bajo") if principal else "bajo"
            self.agregar_clausula(
                id=cid,
                tipo=tipo_mostrado,
                texto=cl.get("texto", ""),
                severidad=severidad,
                tipo_base=tipo_base,
                tipo_riesgo_principal=tipo_mostrado,
                articulo_referencia=principal.get("articulo_violado") if principal else None,
                recomendacion=self._recomendacion_por_hallazgo(principal),
                descripcion_riesgo=principal.get("descripcion_riesgo") if principal else None,
                hallazgos=hallazgos_clausula,
            )

    def _hallazgo_principal(self, hallazgos: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not hallazgos:
            return None
        return max(
            hallazgos,
            key=lambda item: (
                self._SEVERIDAD_RANK.get(str(item.get("severidad", "bajo")).lower(), 0),
                0 if str(item.get("tipo_riesgo", "general")) != "general" else -1,
            ),
        )

    def _recomendacion_por_hallazgo(self, hallazgo: dict[str, Any] | None) -> str | None:
        if not hallazgo:
            return None
        tipo = str(hallazgo.get("tipo_riesgo", "general"))
        recomendaciones = {
            "jornada": "Eliminar exigencias de disponibilidad permanente y fijar horarios, guardias y tiempos de respuesta razonables.",
            "remuneracion_abusiva": "Exigir un plazo de pago razonable, limitar descuentos y eliminar retrabajos sin contraprestacion.",
            "modificacion_unilateral": "Eliminar facultades de cambio unilateral y exigir aprobacion expresa de ambas partes.",
            "arbitraje": "Equilibrar la solucion de controversias y evitar renuncias anticipadas a la via judicial.",
            "propiedad_intelectual": "Delimitar el alcance, plazo, territorio y contraprestacion de la cesion de derechos.",
            "no_competencia": "Reducir tiempo y alcance geografico, e incluir compensacion economica proporcional.",
            "penalidad": "Fijar topes razonables y evitar penalidades automaticas o desproporcionadas.",
            "rescision": "Exigir causal objetiva, preaviso y efectos equilibrados para ambas partes.",
            "datos_personales": "Restringir el tratamiento de datos a finalidades validas y con consentimiento o base legal.",
            "general": "Revisar y renegociar esta clausula antes de firmar para restablecer el equilibrio contractual.",
        }
        return recomendaciones.get(tipo, recomendaciones["general"])

    def clausulas_riesgosas(self) -> List[Clausula]:
        return [c for c in self.clausulas if c.severidad in ("alto", "critico")]

    def to_dict(self) -> dict:
        return {
            "contrato_id": self.contrato_id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "fecha_analisis": self.fecha_analisis,
            "total_clausulas": len(self.clausulas),
            "clausulas": [c.to_json() for c in self.clausulas],
        }


class Dictamen:
    _DESCUENTOS = {"bajo": 5, "medio": 15, "alto": 25, "critico": 40}

    def __init__(self, contrato: Contrato, estadisticas: dict):
        self.contrato = contrato
        self.estadisticas = estadisticas
        self.score = self._calcular_score()
        self.nivel = self._determinar_nivel()

    def _conteo_severidades(self) -> dict:
        conteo = {"bajo": 0, "medio": 0, "alto": 0, "critico": 0}
        for clausula in self.contrato.clausulas:
            severidad = clausula.severidad.lower()
            if severidad in conteo:
                conteo[severidad] += 1
        return conteo

    def _calcular_score(self) -> int:
        score = 100
        for clausula in self.contrato.clausulas:
            score -= self._DESCUENTOS.get(clausula.severidad, 0)

        conteo = self._conteo_severidades()
        total = max(len(self.contrato.clausulas), 1)
        criticos = conteo["critico"]
        altos = conteo["alto"]
        medios = conteo["medio"]
        densidad_riesgo = (criticos * 2.0 + altos * 1.25 + medios * 0.5) / total

        # Guardrails: un contrato con riesgo severo nunca debe verse "seguro".
        if criticos >= 2:
            score = min(score, 15)
        elif criticos == 1:
            score = min(score, 35)
        elif altos >= 2:
            score = min(score, 50)
        elif altos == 1 and medios >= 1:
            score = min(score, 60)
        elif medios >= 3:
            score = min(score, 70)

        score -= int(densidad_riesgo * 10)
        return max(score, 0)

    def _determinar_nivel(self) -> str:
        conteo = self._conteo_severidades()
        criticos = conteo["critico"]
        altos = conteo["alto"]
        medios = conteo["medio"]

        if criticos >= 1:
            return "CRITICO"
        if altos >= 2 or (altos >= 1 and medios >= 1):
            return "ALTO"
        if altos >= 1 or medios >= 2:
            return "MEDIO"
        if self.score < 40:
            return "CRITICO"
        if self.score < 60:
            return "ALTO"
        if self.score < 80:
            return "MEDIO"
        return "BAJO"

    def _recomendacion_final(self) -> str:
        mensajes = {
            "CRITICO": "Contrato con riesgos criticos. NO firmar ni aceptar sus terminos sin correcciones y revision legal urgente.",
            "ALTO":    "Contrato con riesgos significativos. No deberia considerarse justo hasta renegociar las clausulas observadas.",
            "MEDIO":   "Contrato con riesgos moderados. Requiere revision y ajuste antes de considerarlo equilibrado.",
            "BAJO":    "Contrato con bajo nivel de riesgo. Aun asi, conviene revisar los detalles antes de firmar.",
        }
        return mensajes[self.nivel]

    def resumen(self) -> dict:
        return {
            "contrato_id": self.contrato.contrato_id,
            "nombre": self.contrato.nombre,
            "categoria": self.contrato.categoria,
            "fecha_analisis": self.contrato.fecha_analisis,
            "score": self.score,
            "nivel_riesgo": self.nivel,
            "recomendacion_final": self._recomendacion_final(),
            "estadisticas": self.estadisticas,
            "clausulas_riesgosas": len(self.contrato.clausulas_riesgosas()),
            "total_clausulas": len(self.contrato.clausulas),
        }
