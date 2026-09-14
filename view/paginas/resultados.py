"""Pantalla de resultados del analisis.

Autor: GPT-5.4
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from controller.analisis.reportes import generar_reporte, generar_reporte_texto
from view.componentes.badge_riesgo import mostrar_badge
from view.componentes.descarga_reporte import mostrar_descarga


def _gauge(score: int) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Score de seguridad"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0d6efd"},
                "steps": [
                    {"range": [0, 40], "color": "#dc3545"},
                    {"range": [40, 60], "color": "#fd7e14"},
                    {"range": [60, 80], "color": "#ffc107"},
                    {"range": [80, 100], "color": "#28a745"},
                ],
            },
        )
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=60, b=10))
    return fig


def mostrar() -> None:
    st.title("Resultados del Análisis")
    resultado = st.session_state.get("ultimo_resultado")
    lote = st.session_state.get("ultimo_lote")

    if lote and lote.get("resultados"):
        opciones = {f"{r['nombre']} ({r['contrato_id']})": r for r in lote["resultados"]}
        seleccion = st.selectbox("Resultado a visualizar", list(opciones.keys()))
        resultado = opciones[seleccion]

        st.subheader("Comparativo del lote")
        st.dataframe(pd.DataFrame(lote["comparativo"]), use_container_width=True, hide_index=True)

    if not resultado:
        st.info("No hay resultados aún. Ve a `Cargar Contrato` primero.")
        return

    st.subheader(f"{resultado['nombre']} · {resultado['contrato_id']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", resultado["score"])
    c2.metric("Nivel", resultado["nivel_riesgo"])
    c3.metric("Cláusulas", resultado["total_clausulas"])
    c4.metric("Con riesgo", resultado["clausulas_riesgosas"])
    st.info(resultado.get("resumen_ejecutivo", ""))

    col_gauge, col_bar, col_pie = st.columns([1.1, 1, 1])
    col_gauge.plotly_chart(_gauge(int(resultado["score"])), use_container_width=True)

    sev = resultado["estadisticas"].get("severidades", {})
    sev_df = pd.DataFrame({"severidad": list(sev.keys()), "cantidad": list(sev.values())})
    if not sev_df.empty:
        fig_sev = px.bar(
            sev_df,
            x="severidad",
            y="cantidad",
            color="severidad",
            color_discrete_map={
                "bajo": "#28a745",
                "medio": "#ffc107",
                "alto": "#fd7e14",
                "critico": "#dc3545",
            },
            title="Severidades detectadas",
        )
        col_bar.plotly_chart(fig_sev, use_container_width=True)

    tipos = resultado["estadisticas"].get("tipos_clausula", {})
    tipos_df = pd.DataFrame({"tipo": list(tipos.keys()), "cantidad": list(tipos.values())})
    if not tipos_df.empty:
        fig_tipos = px.pie(tipos_df, names="tipo", values="cantidad", hole=0.55, title="Distribución de tipos")
        col_pie.plotly_chart(fig_tipos, use_container_width=True)

    comparacion = resultado.get("comparacion_dataset", {})
    if comparacion:
        st.markdown("### Comparación con dataset de referencia")
        a, b, c = st.columns(3)
        a.metric("Score promedio dataset", comparacion.get("score_promedio_dataset"))
        b.metric("Diferencia vs dataset", comparacion.get("diferencia_score"))
        c.metric("Tipo más frecuente", comparacion.get("tipo_mas_frecuente"))
        if comparacion.get("frecuencias_palabras"):
            st.caption(f"Palabras frecuentes de referencia: {comparacion['frecuencias_palabras']}")

    st.markdown("### Hallazgos")
    if resultado["hallazgos"]:
        for hallazgo in resultado["hallazgos"]:
            mostrar_badge(hallazgo)
    else:
        st.success("No se detectaron hallazgos de riesgo relevantes.")

    st.markdown("### Tabla expandible por cláusula")
    for clausula in resultado["clausulas"]:
        tipo_principal = clausula.get("tipo_riesgo_principal") or clausula.get("tipo")
        tipo_base = clausula.get("tipo_base")
        etiqueta_tipo = f"{tipo_principal}"
        if tipo_base and tipo_base != tipo_principal:
            etiqueta_tipo = f"{tipo_principal} (base: {tipo_base})"
        titulo = f"Cláusula {clausula.get('id')} · {etiqueta_tipo} · {clausula.get('severidad')}"
        with st.expander(titulo):
            st.write(clausula.get("texto", ""))
            st.caption(clausula.get("explicacion", ""))
            st.markdown(f"**Artículo de referencia:** {clausula.get('articulo_referencia', 'N/D')}")
            st.markdown(f"**Recomendación:** {clausula.get('recomendacion', 'N/D')}")
            if clausula.get("hallazgos"):
                st.markdown("**Hallazgos de esta cláusula:**")
                for hallazgo in clausula["hallazgos"]:
                    st.write(
                        f"- {hallazgo.get('tipo_riesgo')} · {hallazgo.get('severidad')} · "
                        f"{hallazgo.get('articulo_violado', 'N/D')}"
                    )

    if resultado.get("anomalias"):
        st.markdown("### Anomalías estadísticas")
        st.dataframe(pd.DataFrame(resultado["anomalias"]), use_container_width=True, hide_index=True)

    st.markdown("### Exportaciones")
    mostrar_descarga(resultado)
    st.download_button(
        "Copiar reporte JSON rápido",
        data=generar_reporte(resultado),
        file_name=f"reporte_rapido_{resultado['contrato_id']}.json",
        mime="application/json",
        use_container_width=True,
    )
    st.download_button(
        "Copiar reporte TXT rápido",
        data=generar_reporte_texto(resultado),
        file_name=f"reporte_rapido_{resultado['contrato_id']}.txt",
        mime="text/plain",
        use_container_width=True,
    )
