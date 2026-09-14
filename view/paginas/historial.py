"""Pantalla de historial de auditorias.

Autor: GPT-5.4
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from controller.almacenamiento.lector_csv import (
    eliminar_auditoria,
    eliminar_hallazgos,
    leer_auditorias,
)
from controller.almacenamiento.lector_json import eliminar_contrato_procesado, obtener_contrato_procesado


def _valor_legible(valor, default: str = "N/D") -> str:
    if pd.isna(valor):
        return default
    texto = str(valor).strip()
    return texto if texto else default


def mostrar() -> None:
    st.title("Historial de Auditorías")
    df = leer_auditorias()
    if df.empty:
        st.info("No hay auditorías registradas aún.")
        return

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    niveles = ["(todos)"] + sorted(df["nivel_riesgo"].dropna().astype(str).unique().tolist()) if "nivel_riesgo" in df else ["(todos)"]
    nivel = st.selectbox("Filtrar por nivel", niveles)
    fecha_inicio, fecha_fin = st.columns(2)
    desde = fecha_inicio.date_input("Desde", value=df["fecha"].min().date() if df["fecha"].notna().any() else None)
    hasta = fecha_fin.date_input("Hasta", value=df["fecha"].max().date() if df["fecha"].notna().any() else None)

    filtrado = df.copy()
    if nivel != "(todos)" and "nivel_riesgo" in filtrado:
        filtrado = filtrado[filtrado["nivel_riesgo"].astype(str) == nivel]
    if "fecha" in filtrado:
        filtrado = filtrado[
            (filtrado["fecha"].dt.date >= desde) &
            (filtrado["fecha"].dt.date <= hasta)
        ]

    tam = st.selectbox("Registros por página", [5, 10, 20, 50], index=1)
    paginas = max(1, (len(filtrado) + tam - 1) // tam)
    pagina = st.number_input("Página", min_value=1, max_value=paginas, value=1, step=1)
    inicio = (pagina - 1) * tam
    subset = filtrado.iloc[inicio : inicio + tam]

    st.dataframe(subset, use_container_width=True, hide_index=True)
    st.caption(f"Mostrando {len(subset)} de {len(filtrado)} auditorías filtradas.")

    st.markdown("### Acciones")
    for _, fila in subset.iterrows():
        col1, col2, col3 = st.columns([4, 1, 1])
        fila_key = f"{fila.name}_{fila.get('contrato_id', 'na')}"
        contrato_id = _valor_legible(fila.get("contrato_id"), "sin_id")
        nombre = _valor_legible(fila.get("nombre"), f"Contrato {contrato_id}")
        score = _valor_legible(fila.get("score"))
        nivel_riesgo = _valor_legible(fila.get("nivel_riesgo"))
        col1.markdown(
            f"**{nombre}** | {contrato_id} | Score {score} | Nivel {nivel_riesgo}"
        )
        if col2.button("Ver detalle", key=f"ver_{fila_key}"):
            detalle = obtener_contrato_procesado(contrato_id)
            if detalle:
                st.session_state["ultimo_resultado"] = detalle
                st.success("Detalle cargado. Ve a `Resultados`.")
        if col3.button("Eliminar", key=f"del_{fila_key}"):
            eliminar_auditoria(contrato_id)
            eliminar_hallazgos(contrato_id)
            eliminar_contrato_procesado(contrato_id)
            st.warning(f"Registro {contrato_id} eliminado.")
            st.rerun()
