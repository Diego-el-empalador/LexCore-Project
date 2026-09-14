"""Pantalla de inicio de LexCore.

Autor: GPT-5.4
"""

import pandas as pd
import streamlit as st

from controller.almacenamiento.lector_csv import leer_auditorias
from model.python.analisis.analizador import cargar_dataset_referencia

_EJEMPLO = """CLÁUSULA I. OBJETO
El proveedor prestará servicios de consultoría tecnológica durante doce meses.

CLÁUSULA II. DATOS PERSONALES
El cliente podrá compartir datos personales y biométricos de sus usuarios con terceros sin consentimiento adicional.

CLÁUSULA III. MODIFICACIÓN UNILATERAL
El cliente podrá modificar unilateralmente el alcance, plazo y precio del servicio sin acuerdo del proveedor.

CLÁUSULA IV. ARBITRAJE
Toda controversia será resuelta solo por arbitraje privado obligatorio renunciando a la vía judicial.
"""


def _logo_svg() -> str:
    return """
    <svg width="92" height="92" viewBox="0 0 92 92" xmlns="http://www.w3.org/2000/svg">
      <circle cx="46" cy="46" r="44" fill="#0d6efd" opacity="0.08"/>
      <path d="M46 18 L46 70" stroke="#0d6efd" stroke-width="4" stroke-linecap="round"/>
      <path d="M24 30 H68" stroke="#0d6efd" stroke-width="4" stroke-linecap="round"/>
      <path d="M30 30 L20 48 H40 Z" fill="#0d6efd" opacity="0.85"/>
      <path d="M62 30 L52 48 H72 Z" fill="#0d6efd" opacity="0.85"/>
      <rect x="32" y="70" width="28" height="6" rx="3" fill="#0d6efd"/>
    </svg>
    """


def mostrar() -> None:
    auditorias = leer_auditorias()
    dataset = cargar_dataset_referencia()
    total_analizados = int(len(auditorias))
    promedio_score = 0.0
    if not auditorias.empty and "score" in auditorias:
        scores = pd.to_numeric(auditorias["score"], errors="coerce").dropna()
        promedio_score = round(float(scores.mean()), 2) if not scores.empty else 0.0
    tipo_mas_frecuente = "N/D"
    if not auditorias.empty and "categoria" in auditorias:
        categorias = auditorias["categoria"].dropna().astype(str).str.strip()
        categorias = categorias[categorias != ""]
        if not categorias.empty:
            tipo_mas_frecuente = str(categorias.value_counts().idxmax())

    col_logo, col_texto = st.columns([1, 5])
    col_logo.markdown(_logo_svg(), unsafe_allow_html=True)
    col_texto.markdown('<div class="main-title">LexCore</div>', unsafe_allow_html=True)
    col_texto.markdown(
        '<div class="subtitle">Auditoría legal inteligente de contratos con razonamiento híbrido Scala → Prolog → Python.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Contratos analizados", total_analizados)
    c2.metric("Score promedio", promedio_score)
    c3.metric("Tipo más frecuente", tipo_mas_frecuente)
    c4.metric("Registros referencia", dataset["total_registros"])

    st.markdown("### Qué hace LexCore")
    col1, col2, col3 = st.columns(3)
    col1.markdown('<div class="lexcore-card"><b>Scala</b><br/>Segmenta y tokeniza cláusulas con enfoque funcional.</div>', unsafe_allow_html=True)
    col2.markdown('<div class="lexcore-card"><b>Prolog</b><br/>Razona con reglas legales y detecta cláusulas abusivas.</div>', unsafe_allow_html=True)
    col3.markdown('<div class="lexcore-card"><b>Python + Streamlit</b><br/>Orquesta el pipeline, compara contra dataset y visualiza resultados.</div>', unsafe_allow_html=True)

    st.markdown("### Ejemplo rápido")
    st.code(_EJEMPLO, language="text")
    if st.button("Usar ejemplo en Cargar Contrato", type="primary"):
        st.session_state["ejemplo_contrato"] = _EJEMPLO
        st.session_state["ejemplo_nombre"] = "Contrato Demo Servicios"
        st.success("Ejemplo cargado. Ve a `Cargar Contrato` para analizarlo.")
