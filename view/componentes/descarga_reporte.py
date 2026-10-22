"""Controles de descarga para reportes del analisis.

Autor: GPT-5.4
"""

import streamlit as st

from controller.analisis.reportes import (
    generar_reporte,
    generar_reporte_pdf,
    generar_reporte_texto,
    generar_reporte_xlsx,
)

from controller.utils.logger import get_logger

logger = get_logger(__name__)


def _generar_seguro(generador, resultado: dict, etiqueta: str):
    """Ejecuta un exportador; si falla, avisa y deja seguir con Resultados."""
    try:
        return generador(resultado)
    except Exception as exc:  # noqa: BLE001 - un export nunca debe bloquear la pantalla
        logger.error(f"Fallo al generar reporte {etiqueta}: {exc}")
        st.warning(f"No se pudo generar el reporte {etiqueta}. El resto de Resultados sigue disponible.")
        return None


def mostrar_descarga(resultado: dict) -> None:
    reporte_json = _generar_seguro(generar_reporte, resultado, "JSON")
    reporte_texto = _generar_seguro(generar_reporte_texto, resultado, "TXT")
    reporte_pdf = _generar_seguro(generar_reporte_pdf, resultado, "PDF")
    reporte_xlsx = _generar_seguro(generar_reporte_xlsx, resultado, "XLSX")

    col1, col2 = st.columns(2)
    col1.download_button(
        label="Descargar reporte JSON",
        data=reporte_json if reporte_json is not None else b"",
        disabled=reporte_json is None,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.json",
        mime="application/json",
        use_container_width=True,
    )
    col2.download_button(
        label="Descargar reporte TXT",
        data=reporte_texto if reporte_texto is not None else b"",
        disabled=reporte_texto is None,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    col3, col4 = st.columns(2)
    col3.download_button(
        label="Descargar reporte PDF",
        data=reporte_pdf if reporte_pdf is not None else b"",
        disabled=reporte_pdf is None,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    col4.download_button(
        label="Descargar reporte XLSX",
        data=reporte_xlsx if reporte_xlsx is not None else b"",
        disabled=reporte_xlsx is None,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )