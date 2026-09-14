"""Pantalla de estadisticas globales e historicas.

Autor: GPT-5.4
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from controller.almacenamiento.lector_csv import leer_auditorias, leer_hallazgos
from model.python.analisis.analizador import cargar_dataset_referencia


def mostrar() -> None:
    st.title("Estadísticas Globales")
    df_aud = leer_auditorias()
    df_hal = leer_hallazgos()
    dataset = cargar_dataset_referencia()
    df_ref = dataset["dataframe"]

    a, b, c, d = st.columns(4)
    a.metric("Contratos analizados", len(df_aud))
    b.metric("Total hallazgos", len(df_hal))
    c.metric("Registros dataset", dataset["total_registros"])
    d.metric("% abusivas referencia", dataset["porcentaje_abusivas"])

    if not df_aud.empty and "fecha" in df_aud:
        df_aud["fecha"] = pd.to_datetime(df_aud["fecha"], errors="coerce")
        y_col = None
        title = None
        if "score" in df_aud:
            df_aud["score"] = pd.to_numeric(df_aud["score"], errors="coerce")
            if df_aud["score"].notna().any():
                y_col = "score"
                title = "Evolución de scores"
        if y_col is None and "clausulas_riesgo" in df_aud:
            df_aud["clausulas_riesgo"] = pd.to_numeric(df_aud["clausulas_riesgo"], errors="coerce")
            if df_aud["clausulas_riesgo"].notna().any():
                y_col = "clausulas_riesgo"
                title = "Evolución de cláusulas con riesgo"
        if y_col is None:
            st.info("El historial no tiene columna de score (o está vacía).")
        else:
            fig = px.line(df_aud.sort_values("fecha"), x="fecha", y=y_col, markers=True, title=title)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aún no hay historial suficiente para graficar evolución.")

    col1, col2 = st.columns(2)
    if dataset["top_riesgos"]:
        top_df = pd.DataFrame(
            {"tipo_clausula": list(dataset["top_riesgos"].keys()), "cantidad": list(dataset["top_riesgos"].values())}
        )
        col1.plotly_chart(
            px.bar(top_df, x="tipo_clausula", y="cantidad", title="Top 5 cláusulas más riesgosas (dataset)"),
            use_container_width=True,
        )

    if not df_hal.empty and {"tipo_riesgo", "severidad"}.issubset(df_hal.columns):
        heat = df_hal.pivot_table(
            index="tipo_riesgo",
            columns="severidad",
            values="clausula_id",
            aggfunc="count",
            fill_value=0,
        )
        col2.plotly_chart(
            px.imshow(heat, text_auto=True, aspect="auto", title="Heatmap severidad por tipo de cláusula"),
            use_container_width=True,
        )

    st.markdown("### Dataset de referencia")
    if not df_ref.empty:
        ref1, ref2 = st.columns(2)
        ref1.plotly_chart(
            px.pie(
                names=list(dataset["tipos_contrato"].keys()),
                values=list(dataset["tipos_contrato"].values()),
                hole=0.45,
                title="Distribución por tipo de contrato",
            ),
            use_container_width=True,
        )
        ref2.plotly_chart(
            px.bar(
                x=list(dataset["severidades"].keys()),
                y=list(dataset["severidades"].values()),
                color=list(dataset["severidades"].keys()),
                title="Severidades del dataset",
            ),
            use_container_width=True,
        )
        st.dataframe(df_ref.head(20), use_container_width=True, hide_index=True)
