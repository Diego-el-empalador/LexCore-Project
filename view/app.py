# Módulo de Interfaz Gráfica - LexCore (Streamlit)
# Desarrollado para gestión y análisis documental
"""Aplicacion principal Streamlit de LexCore.

Autor: GPT-5.4
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from view.paginas import cargar_contrato, estadisticas, historial, inicio, resultados

st.set_page_config(
    page_title="LexCore",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem;}
    .subtitle {color: #5f6368; margin-bottom: 1rem;}
    .lexcore-card {
        border: 1px solid rgba(49, 51, 63, 0.15);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        background: rgba(255,255,255,0.03);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "ejemplo_contrato" not in st.session_state:
    st.session_state["ejemplo_contrato"] = ""

PAGINAS = {
    "Inicio": inicio,
    "Cargar Contrato": cargar_contrato,
    "Resultados": resultados,
    "Historial": historial,
    "Estadísticas": estadisticas,
}

st.sidebar.markdown("## LexCore")
st.sidebar.caption("Auditoría legal inteligente de contratos con Scala, Prolog y Python")
st.sidebar.info(
    "Pipeline activo:\n\n- Tokenización: Scala\n- Razonamiento: Prolog\n- Analítica: Python/pandas/numpy\n- UI: Streamlit + Plotly"
)
seleccion = st.sidebar.radio("Navegación", list(PAGINAS.keys()))
PAGINAS[seleccion].mostrar()
