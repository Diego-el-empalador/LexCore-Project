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


def mostrar_descarga(resultado: dict) -> None:
    reporte_json = generar_reporte(resultado)
    reporte_texto = generar_reporte_texto(resultado)
    reporte_pdf = generar_reporte_pdf(resultado)
    reporte_xlsx = generar_reporte_xlsx(resultado)

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

    col3, col4 = st.columns(2)
    col3.download_button(
        label="Descargar reporte PDF",
        data=reporte_pdf,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    col4.download_button(
        label="Descargar reporte XLSX",
        data=reporte_xlsx,
        file_name=f"reporte_{resultado.get('contrato_id', 'lexcore')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )