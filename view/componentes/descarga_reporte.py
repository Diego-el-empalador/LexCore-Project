"""Controles de descarga para reportes del analisis.

Autor: GPT-5.4
"""

import streamlit as st

from controller.analisis.reportes import generar_reporte, generar_reporte_texto


def mostrar_descarga(resultado: dict) -> None:
    reporte_json = generar_reporte(resultado)
    reporte_texto = generar_reporte_texto(resultado)
    col1, col2 = st.columns(2)
    col1.download_button(
        label="Descargar reporte JSON",
        data=reporte_json,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.json",
        mime="application/json",
        use_container_width=True,
    )
    col2.download_button(
        label="Descargar reporte TXT",
        data=reporte_texto,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.txt",
        mime="text/plain",
        use_container_width=True,
    )
