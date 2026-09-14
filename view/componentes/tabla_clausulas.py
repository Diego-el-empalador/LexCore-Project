"""Tabla paginada y filtrable para cláusulas.

Autor: GPT-5.4
"""

import pandas as pd
import streamlit as st

def mostrar_tabla(clausulas: list[dict]) -> None:
    if not clausulas:
        st.warning("No se encontraron cláusulas.")
        return

    busqueda = st.text_input("Buscar en texto", value="", placeholder="Ej: multa, plazo, confidencialidad", key="tabla_clausulas_busqueda")
    tipos = sorted({str(c.get("tipo", "general")) for c in clausulas})
    filtro_tipo = st.selectbox("Tipo", ["(todos)"] + tipos, index=0, key="tabla_clausulas_tipo")
    tam_pagina = st.selectbox("Filas por página", [50, 100, 200, 500], index=0, key="tabla_clausulas_tam")

    filtradas = clausulas
    if filtro_tipo != "(todos)":
        filtradas = [c for c in filtradas if str(c.get("tipo", "general")) == filtro_tipo]
    if busqueda.strip():
        q = busqueda.strip().lower()
        filtradas = [c for c in filtradas if q in str(c.get("texto", "")).lower()]

    total = len(filtradas)
    if total == 0:
        st.info("No hay coincidencias con los filtros.")
        return

    paginas = max(1, (total + tam_pagina - 1) // tam_pagina)
    pagina = st.number_input("Página", min_value=1, max_value=paginas, value=1, step=1, key="tabla_clausulas_pagina")
    inicio = (pagina - 1) * tam_pagina
    fin = min(inicio + tam_pagina, total)
    st.caption(f"Mostrando {inicio + 1}-{fin} de {total} cláusulas.")

    df = pd.DataFrame([
        {
            "ID": c.get("id"),
            "Tipo": c.get("tipo"),
            "Texto (extracto)": (str(c.get("texto", ""))[:120] + "...") if str(c.get("texto", "")) else "",
        }
        for c in filtradas[inicio:fin]
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
