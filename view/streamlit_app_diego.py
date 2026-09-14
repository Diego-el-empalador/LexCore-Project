import streamlit as st
import pandas as pd
import plotly.express as px
import time
import json
import os
from datetime import datetime

# ========== CONFIGURACIÓN ==========
st.set_page_config(
    page_title="LexCore - Auditor Legal",
    page_icon=":material/gavel:",
    layout="wide"
)

# ========== CSS MEJORADO ==========
st.markdown("""
    <style>
    /* Mejora de métricas */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 10px;
    }
    
    /* Botón principal */
    .stButton > button {
        background: linear-gradient(120deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
    }
    
    /* Mejora de tablas */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# Crear carpetas
os.makedirs("data/historial", exist_ok=True)

# ========== FUNCIONES ==========
def guardar_historial(contrato, score, dictamen, clausulas):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    historial = {
        "fecha": timestamp,
        "contrato": contrato[:200],
        "score": score,
        "dictamen": dictamen,
        "clausulas": clausulas
    }
    with open(f"data/historial/{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2, ensure_ascii=False)
    return timestamp

def cargar_historial():
    historial = []
    if os.path.exists("data/historial"):
        for archivo in os.listdir("data/historial"):
            if archivo.endswith(".json"):
                with open(f"data/historial/{archivo}", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    historial.append(data)
    historial.sort(key=lambda x: x["fecha"], reverse=True)
    return historial

def analizar_contrato_simulado(contrato_texto):
    clausulas = []
    score_inicial = 100
    
    # Detección de salario
    if "s/" in contrato_texto.lower() or "salario" in contrato_texto.lower():
        import re
        numeros = re.findall(r'\d+', contrato_texto)
        encontrado = False
        for num in numeros:
            if int(num) < 1025 and int(num) > 500:
                clausulas.append({
                    "clausula": f"Salario de S/ {num} mensuales",
                    "tipo": "Salario",
                    "abusiva": True,
                    "fundamento": "Art. 5°: La RMV es S/ 1025"
                })
                score_inicial -= 25
                encontrado = True
                break
        if not encontrado:
            clausulas.append({
                "clausula": "Salario pactado",
                "tipo": "Salario",
                "abusiva": False,
                "fundamento": "Salario conforme a ley"
            })
    else:
        clausulas.append({
            "clausula": "No se encontró cláusula de salario",
            "tipo": "Salario",
            "abusiva": False,
            "fundamento": "No se puede verificar"
        })
    
    # Detección de jornada
    if "hora" in contrato_texto.lower():
        import re
        numeros = re.findall(r'\d+', contrato_texto)
        encontrado = False
        for num in numeros:
            if int(num) > 48 and int(num) < 100:
                clausulas.append({
                    "clausula": f"Jornada de {num} horas semanales",
                    "tipo": "Jornada",
                    "abusiva": True,
                    "fundamento": "Art. 24°: Máximo 48 horas semanales"
                })
                score_inicial -= 25
                encontrado = True
                break
        if not encontrado:
            clausulas.append({
                "clausula": "Jornada laboral",
                "tipo": "Jornada",
                "abusiva": False,
                "fundamento": "Jornada conforme a ley"
            })
    else:
        clausulas.append({
            "clausula": "No se encontró cláusula de jornada",
            "tipo": "Jornada",
            "abusiva": False,
            "fundamento": "No se puede verificar"
        })
    
    # Detección de periodo de prueba
    if "prueba" in contrato_texto.lower() or "meses" in contrato_texto.lower():
        import re
        numeros = re.findall(r'\d+', contrato_texto)
        encontrado = False
        for num in numeros:
            if int(num) > 3 and int(num) < 12:
                clausulas.append({
                    "clausula": f"Periodo de prueba de {num} meses",
                    "tipo": "Periodo Prueba",
                    "abusiva": True,
                    "fundamento": "Art. 10°: Máximo 3 meses"
                })
                score_inicial -= 25
                encontrado = True
                break
        if not encontrado:
            clausulas.append({
                "clausula": "Periodo de prueba",
                "tipo": "Periodo Prueba",
                "abusiva": False,
                "fundamento": "Periodo conforme a ley"
            })
    else:
        clausulas.append({
            "clausula": "No se encontró cláusula de periodo de prueba",
            "tipo": "Periodo Prueba",
            "abusiva": False,
            "fundamento": "No se puede verificar"
        })
    
    # Detección de descuentos
    if "descuento" in contrato_texto.lower() or "uniforme" in contrato_texto.lower():
        clausulas.append({
            "clausula": "Descuento por uniforme o herramientas",
            "tipo": "Descuento",
            "abusiva": True,
            "fundamento": "Art. 42°: Descuentos prohibidos"
        })
        score_inicial -= 25
    else:
        clausulas.append({
            "clausula": "Descuentos",
            "tipo": "Descuento",
            "abusiva": False,
            "fundamento": "Sin descuentos abusivos detectados"
        })
    
    # Determinar dictamen
    if score_inicial <= 40:
        dictamen = "ALTO"
    elif score_inicial <= 70:
        dictamen = "MEDIO"
    else:
        dictamen = "BAJO"
    
    return max(0, score_inicial), dictamen, clausulas

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### :material/gavel: LexCore")
    st.divider()
    
    historial = cargar_historial()
    
    with st.container(border=True):
        st.markdown("#### :material/analytics: Estadísticas")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total", len(historial), border=True)
        with c2:
            if historial:
                promedio = sum(h["score"] for h in historial) // len(historial)
                st.metric("Promedio", f"{promedio}/100", border=True)
    
    st.divider()
    
    st.markdown("#### :material/history: Últimas auditorías")
    for h in historial[:5]:
        if h["dictamen"] == "ALTO":
            icono = ":material/warning:"
        elif h["dictamen"] == "MEDIO":
            icono = ":material/info:"
        else:
            icono = ":material/check_circle:"
        st.caption(f"{icono} {h['fecha'][:10]} - {h['score']}/100")
    
    st.divider()
    st.caption(":material/scale: LexCore v1.0")

# ========== CONTENIDO PRINCIPAL ==========
st.title(":material/gavel: LexCore - Auditor Inteligente de Contratos")
st.caption("*Sistema profesional de detección de cláusulas abusivas en contratos laborales*")

st.divider()

# Área de carga
st.markdown("#### :material/description: Cargar Contrato")
contrato = st.text_area("", placeholder="Pega aquí el texto completo de tu contrato laboral...", height=150)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    auditar = st.button(":material/scale: Auditar Contrato", type="primary", use_container_width=True)

# ========== RESULTADOS ==========
if auditar and contrato:
    with st.spinner(":material/sync: Analizando contrato..."):
        time.sleep(1.5)
        score, dictamen, clausulas = analizar_contrato_simulado(contrato)
        timestamp = guardar_historial(contrato, score, dictamen, clausulas)
    
    st.success(":material/check_circle: Auditoría completada exitosamente")
    
    # Métricas
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        if score >= 70:
            delta_score = "Contrato seguro"
            icon_score = ":material/verified:"
        elif score >= 40:
            delta_score = "Requiere revisión"
            icon_score = ":material/info:"
        else:
            delta_score = "¡Alto riesgo detectado!"
            icon_score = ":material/warning:"
        
        st.metric(
            label=f"{icon_score} Score de Seguridad",
            value=f"{score}/100",
            delta=delta_score,
            border=True
        )
    
    with col_m2:
        if dictamen == "BAJO":
            color_dict = "🟢 BAJO"
            icon_dict = ":material/check_circle:"
        elif dictamen == "MEDIO":
            color_dict = "🟡 MEDIO"
            icon_dict = ":material/info:"
        else:
            color_dict = "🔴 ALTO"
            icon_dict = ":material/error:"
        
        st.metric(
            label=f"{icon_dict} Dictamen Legal",
            value=color_dict,
            border=True
        )
    
    # Gráfico
    st.markdown("#### :material/pie_chart: Distribución de Cláusulas")
    abusivas = sum(1 for c in clausulas if c["abusiva"])
    conformes = len(clausulas) - abusivas
    
    fig = px.pie(
        values=[abusivas, conformes],
        names=['❌ Abusivas', '✅ Conformes'],
        title=f'Total: {len(clausulas)} cláusulas analizadas',
        color_discrete_sequence=['#dc3545', '#28a745'],
        hole=0.4
    )
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig, use_container_width=True)
    
    # ========== TABLA ARREGLADA ==========
    st.markdown("#### :material/format_list_bulleted: Detalle de Cláusulas Analizadas")
    
    # Crear DataFrame limpio
    df_tabla = pd.DataFrame(clausulas)
    
    # Renombrar columnas
    df_tabla = df_tabla.rename(columns={
        "clausula": "📝 Texto de la Cláusula",
        "tipo": "🏷️ Tipo",
        "fundamento": "⚖️ Fundamento Legal"
    })
    
    # Agregar columna de estado
    df_tabla["🔍 Estado"] = df_tabla["abusiva"].apply(
        lambda x: "❌ ABUSIVA" if x else "✅ CONFORME"
    )
    
    # Eliminar columna original abusiva
    df_tabla = df_tabla.drop(columns=["abusiva"])
    
    # Reordenar
    df_tabla = df_tabla[["📝 Texto de la Cláusula", "🏷️ Tipo", "🔍 Estado", "⚖️ Fundamento Legal"]]
    
    # Colorear filas
    def colorear_fila(row):
        if "ABUSIVA" in row["🔍 Estado"]:
            return ['background-color: #ffcccc; color: #8b0000; font-weight: bold'] * len(row)
        else:
            return ['background-color: #ccffcc; color: #006400; font-weight: bold'] * len(row)
    
    df_estilizada = df_tabla.style.apply(colorear_fila, axis=1)
    df_estilizada = df_estilizada.set_properties(**{
        'text-align': 'left',
        'padding': '8px'
    })
    
    st.dataframe(df_estilizada, use_container_width=True, hide_index=True)
    
    # Explicación
    with st.expander(":material/psychology: Ver cadena de razonamiento lógico"):
        st.info("""
        **Reglas aplicadas según legislación peruana:**
        
        | Regla | Condición | Estado |
        |-------|-----------|--------|
        | Art. 5° - RMV (S/1025) | Salario < 1025 | ❌ Violación |
        | Art. 24° - Jornada | Horas > 48 | ❌ Violación |
        | Art. 10° - Periodo prueba | Meses > 3 | ❌ Violación |
        | Art. 42° - Descuentos | Descuentos prohibidos | ❌ Violación |
        """)
    
    # Descarga
    st.download_button(
        ":material/download: Descargar Reporte (JSON)",
        data=json.dumps({"score": score, "dictamen": dictamen, "clausulas": clausulas}, indent=2, ensure_ascii=False),
        file_name=f"lexcore_{timestamp}.json",
        mime="application/json",
        use_container_width=True
    )

elif auditar and not contrato:
    st.warning(":material/warning: Por favor, pega un contrato para auditar")