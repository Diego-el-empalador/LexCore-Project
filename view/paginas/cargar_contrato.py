"""Pantalla de carga y procesamiento individual o masivo.

Autor: GPT-5.4
"""

from __future__ import annotations

import io
import re

import streamlit as st

from controller.analisis.reportes import generar_reporte_comparativo_csv
from controller.orquestador.pipeline import analizar_contrato, analizar_lote

try:
    import pdfplumber
except Exception:  # pragma: no cover - depende del entorno local
    pdfplumber = None

TIPOS = {
    "laboral": "Contratos de trabajo, confidencialidad laboral y pactos de no competencia.",
    "arrendamiento": "Arriendos de inmuebles, penalidades, mantenimiento y resolución.",
    "servicios": "Prestación de servicios, alcance, PI, datos y arbitraje.",
    "compraventa": "Precio, entrega, garantías, propiedad y saneamiento.",
}


def _estimar_clausulas(texto: str) -> int:
    return max(
        1,
        len(
            [
                parte
                for parte in re.split(
                    r"(?im)(?=^\s*(?:cl[áa]usula|art[íi]culo|secci[óo]n|[ivxlcdm]+[\.\)]|\d+[\.\)]))",
                    texto,
                )
                if parte.strip()
            ]
        ),
    )


def _leer_archivo(archivo) -> str:
    contenido = archivo.read()
    if archivo.name.lower().endswith(".pdf"):
        if pdfplumber is None:
            raise RuntimeError("pdfplumber no esta instalado para procesar PDFs.")
        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            return "\n".join((pagina.extract_text() or "") for pagina in pdf.pages).strip()
    return contenido.decode("utf-8", errors="replace")


def mostrar() -> None:
    st.title("Cargar Contrato")
    categoria = st.selectbox("Tipo de contrato", list(TIPOS.keys()), help="Selecciona el dominio legal más cercano.")
    st.caption(TIPOS[categoria])

    nombre = st.text_input(
        "Nombre del contrato",
        value=st.session_state.get("ejemplo_nombre", ""),
        placeholder="Ej: Contrato de Arrendamiento 2026",
    )
    metodo = st.radio("Método de carga", ["Pegar texto", "Subir archivos .txt/.pdf"], horizontal=True)

    texto = st.session_state.get("ejemplo_contrato", "") if metodo == "Pegar texto" else ""
    archivos_lote: list[dict[str, str]] = []

    if metodo == "Pegar texto":
        texto = st.text_area("Texto del contrato", value=texto, height=320)
        st.caption(f"Caracteres: {len(texto):,} | Cláusulas estimadas: {_estimar_clausulas(texto) if texto.strip() else 0}")
        if len(texto) > 200_000:
            st.warning("Para textos muy largos, subir archivo suele ser más estable que pegar contenido.")
    else:
        archivos = st.file_uploader(
            "Sube uno o varios contratos",
            type=["txt", "pdf"],
            accept_multiple_files=True,
        )
        if archivos:
            for archivo in archivos:
                texto_archivo = _leer_archivo(archivo)
                archivos_lote.append({"nombre": archivo.name, "texto": texto_archivo})
            seleccionado = st.selectbox("Vista previa", [a["nombre"] for a in archivos_lote])
            preview = next(a["texto"] for a in archivos_lote if a["nombre"] == seleccionado)
            st.text_area(
                "Vista previa del contenido",
                preview[:10000] + ("\n\n...(truncado)..." if len(preview) > 10000 else ""),
                height=240,
                disabled=True,
            )
            st.caption(
                f"Archivos cargados: {len(archivos_lote)} | Caracteres del seleccionado: {len(preview):,} | "
                f"Cláusulas estimadas: {_estimar_clausulas(preview)}"
            )

    progreso = st.progress(0)
    estado = st.empty()

    def callback(mensaje: str, valor: float) -> None:
        progreso.progress(min(max(valor, 0.0), 1.0))
        estado.info(mensaje)

    if st.button("Analizar contrato(s)", type="primary", use_container_width=True):
        try:
            if metodo == "Pegar texto":
                if not nombre or not texto.strip():
                    st.warning("Ingresa el nombre y el texto del contrato.")
                    return
                resultado = analizar_contrato(texto, nombre, categoria=categoria, progreso_callback=callback)
                st.session_state["ultimo_resultado"] = resultado
                st.session_state["ultimo_lote"] = None
                st.success(f"Análisis completado: {len(resultado['hallazgos'])} hallazgo(s).")
            else:
                if not archivos_lote:
                    st.warning("Sube al menos un archivo .txt o .pdf.")
                    return
                lote = analizar_lote(archivos_lote, categoria=categoria, progreso_callback=callback)
                st.session_state["ultimo_lote"] = lote
                st.session_state["ultimo_resultado"] = lote["resultados"][0] if lote["resultados"] else None
                st.success(f"Procesamiento masivo completado: {len(lote['resultados'])} archivo(s).")
                st.download_button(
                    "Descargar reporte comparativo CSV",
                    data=generar_reporte_comparativo_csv(lote["resultados"]),
                    file_name="reporte_comparativo_lexcore.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            estado.success("Proceso finalizado.")
        except Exception as exc:
            estado.empty()
            st.error(f"Error durante el análisis: {exc}")
