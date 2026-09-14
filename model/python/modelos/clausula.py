"""Modelos de clausulas de dominio y enriquecimiento legal.

Autor: GPT-5.4
"""

from __future__ import annotations

from typing import Any


class Clausula:
    NIVELES_RIESGO = {"bajo": 1, "medio": 2, "alto": 3, "critico": 4}
    COLORES = {
        "bajo": "#28a745",
        "medio": "#ffc107",
        "alto": "#fd7e14",
        "critico": "#dc3545",
    }

    def __init__(
        self,
        id: str,
        tipo: str,
        texto: str,
        severidad: str,
        *,
        tipo_base: str | None = None,
        tipo_riesgo_principal: str | None = None,
        articulo_referencia: str | None = None,
        recomendacion: str | None = None,
        descripcion_riesgo: str | None = None,
        hallazgos: list[dict[str, Any]] | None = None,
    ):
        self.id = id
        self.tipo = tipo
        self.tipo_base = tipo_base or tipo
        self.tipo_riesgo_principal = tipo_riesgo_principal or tipo
        self.texto = texto
        self.severidad = severidad.lower()
        self.es_riesgosa = self.severidad in ("alto", "critico")
        self.articulo_referencia = articulo_referencia
        self.recomendacion = recomendacion
        self.descripcion_riesgo = descripcion_riesgo
        self.hallazgos = hallazgos or []

    @property
    def color_severidad(self) -> str:
        return self.COLORES.get(self.severidad, "#6c757d")

    def peso_riesgo(self) -> int:
        return self.NIVELES_RIESGO.get(self.severidad, 1)

    def explicacion_legal(self) -> str:
        if self.descripcion_riesgo:
            return self.descripcion_riesgo
        mensajes = {
            "bajo": "La clausula luce aceptable, aunque conviene verificar que mantenga claridad y equilibrio.",
            "medio": "La clausula requiere revision porque puede generar interpretaciones ambiguas o costos inesperados.",
            "alto": "La clausula presenta un desequilibrio importante y deberia renegociarse antes de firmar.",
            "critico": "La clausula puede vulnerar normas imperativas o derechos de una de las partes; se recomienda detener la firma hasta corregirla.",
        }
        return mensajes.get(self.severidad, mensajes["medio"])

    def to_json(self) -> dict:
        base = self.evaluar()
        base["color_severidad"] = self.color_severidad
        base["explicacion"] = self.explicacion_legal()
        return base

    def evaluar(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "tipo_base": self.tipo_base,
            "tipo_riesgo_principal": self.tipo_riesgo_principal,
            "texto": self.texto,
            "severidad": self.severidad,
            "es_riesgosa": self.es_riesgosa,
            "peso_riesgo": self.peso_riesgo(),
            "hallazgos": self.hallazgos,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} tipo={self.tipo} severidad={self.severidad}>"


class ClausulaLaboral(Clausula):
    _ARTICULOS = {
        "despido":           "Art. 22° LPCL — causa justa de despido",
        "jornada":           "Art. 25° Constitución — jornada máxima 8h",
        "remuneracion":      "Art. 24° Constitución — remuneración equitativa",
        "cese_colectivo":    "Art. 46° LPCL — cese colectivo por causas objetivas",
        "vacaciones":        "Art. 10° D.Leg. 713 — derecho a vacaciones anuales",
        "horas_extra":       "Art. 9° D.Leg. 854 — trabajo en sobretiempo voluntario",
        "default":           "Art. 4° LPCL — contrato de trabajo",
    }

    def evaluar(self) -> dict:
        base = super().evaluar()
        tipo_referencia = (self.tipo_riesgo_principal or self.tipo).lower()
        clave = next((k for k in self._ARTICULOS if k in tipo_referencia), "default")
        base.update({
            "categoria": "laboral",
            "articulo_referencia": self.articulo_referencia or self._ARTICULOS[clave],
            "recomendacion": self.recomendacion or (
                "Verificar cumplimiento de la Ley de Productividad y Competitividad Laboral "
                "y la Constitución Política del Perú (Art. 22°-29°)."
            ),
        })
        return base

    def explicacion_legal(self) -> str:
        return (
            "Esta clausula impacta la relacion laboral y puede comprometer derechos del trabajador, "
            "como remuneracion, estabilidad o proteccion frente a cambios unilaterales."
        )


class ClausulaArrendamiento(Clausula):
    _ARTICULOS = {
        "renta":          "Art. 1666° CC — contrato de arrendamiento",
        "plazo":          "Art. 1688° CC — duración del arrendamiento",
        "conservacion":   "Art. 1681° CC — obligaciones del arrendatario",
        "resolucion":     "Art. 1697° CC — resolución del contrato",
        "subarrendamiento": "Art. 1692° CC — subarrendamiento",
        "default":        "Art. 1666° CC — arrendamiento de bienes",
    }

    def evaluar(self) -> dict:
        base = super().evaluar()
        tipo_referencia = (self.tipo_riesgo_principal or self.tipo).lower()
        clave = next((k for k in self._ARTICULOS if k in tipo_referencia), "default")
        base.update({
            "categoria": "arrendamiento",
            "articulo_referencia": self.articulo_referencia or self._ARTICULOS[clave],
            "recomendacion": self.recomendacion or (
                "Revisar las obligaciones del arrendador y arrendatario conforme "
                "al Código Civil Peruano (Arts. 1666°-1712°)."
            ),
        })
        return base

    def explicacion_legal(self) -> str:
        return (
            "La clausula afecta el equilibrio entre arrendador y arrendatario; debe revisar plazo, penalidades, "
            "resolucion y uso de datos para evitar abusos."
        )


class ClausulaServicios(Clausula):
    _ARTICULOS = {
        "honorarios":     "Art. 1764° CC — contrato de locación de servicios",
        "plazo":          "Art. 1768° CC — duración del contrato de servicios",
        "obligaciones":   "Art. 1766° CC — obligaciones del locador",
        "resolucion":     "Art. 1786° CC — resolución por incumplimiento",
        "confidencial":   "Art. 1770° CC — deber de reserva profesional",
        "default":        "Art. 1764° CC — locación de servicios",
    }

    def evaluar(self) -> dict:
        base = super().evaluar()
        tipo_referencia = (self.tipo_riesgo_principal or self.tipo).lower()
        clave = next((k for k in self._ARTICULOS if k in tipo_referencia), "default")
        base.update({
            "categoria": "servicios",
            "articulo_referencia": self.articulo_referencia or self._ARTICULOS[clave],
            "recomendacion": self.recomendacion or (
                "Verificar la naturaleza civil del vínculo para evitar desnaturalización "
                "laboral conforme al Código Civil (Arts. 1764°-1770°)."
            ),
        })
        return base

    def explicacion_legal(self) -> str:
        return (
            "La clausula regula alcance, propiedad intelectual, confidencialidad o datos en servicios; "
            "si es desequilibrada puede generar sobrecostos o cesiones excesivas."
        )


class ClausulaCompraventa(Clausula):
    _ARTICULOS = {
        "precio":         "Art. 1529° CC — contrato de compraventa",
        "entrega":        "Art. 1549° CC — obligación de entrega del bien",
        "saneamiento":    "Art. 1484° CC — saneamiento por evicción",
        "garantia":       "Art. 1503° CC — garantía de buen funcionamiento",
        "resolucion":     "Art. 1562° CC — resolución por falta de pago",
        "propiedad":      "Art. 1529° CC — transferencia de propiedad",
        "default":        "Art. 1529° CC — compraventa de bienes",
    }

    def evaluar(self) -> dict:
        base = super().evaluar()
        tipo_referencia = (self.tipo_riesgo_principal or self.tipo).lower()
        clave = next((k for k in self._ARTICULOS if k in tipo_referencia), "default")
        base.update({
            "categoria": "compraventa",
            "articulo_referencia": self.articulo_referencia or self._ARTICULOS[clave],
            "recomendacion": self.recomendacion or (
                "Confirmar condiciones de transferencia de propiedad y saneamiento "
                "conforme al Código Civil Peruano (Arts. 1529°-1601°)."
            ),
        })
        return base

    def explicacion_legal(self) -> str:
        return (
            "La clausula puede afectar precio, entrega, garantias o transferencia de derechos; "
            "si exonera al vendedor o altera el objeto de venta, el riesgo aumenta."
        )


_FABRICA = {
    "laboral":       ClausulaLaboral,
    "arrendamiento": ClausulaArrendamiento,
    "servicios":     ClausulaServicios,
    "compraventa":   ClausulaCompraventa,
}


def fabricar_clausula(
    categoria: str,
    id: str,
    tipo: str,
    texto: str,
    severidad: str,
    **kwargs: Any,
) -> Clausula:
    cls = _FABRICA.get(categoria.lower(), Clausula)
    return cls(id=id, tipo=tipo, texto=texto, severidad=severidad, **kwargs)
