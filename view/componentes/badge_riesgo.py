"""Componentes visuales para presentar hallazgos de riesgo.

Autor: GPT-5.4
"""

import streamlit as st

_ICONOS = {"critico": "🔴", "alto": "🟠", "medio": "🟡", "bajo": "🟢"}


def mostrar_badge(hallazgo: dict) -> None:
    sev = hallazgo.get("severidad", "bajo")
    icono = _ICONOS.get(sev, "⚪")
    st.markdown(
        f"{icono} **Cláusula {hallazgo.get('clausula_id')}** | "
        f"Riesgo: `{hallazgo.get('tipo_riesgo')}` | Severidad: `{sev}` | "
        f"Artículo: `{hallazgo.get('articulo_violado', 'N/A')}`"
    )
    if hallazgo.get("descripcion_riesgo"):
        st.caption(str(hallazgo.get("descripcion_riesgo")))
