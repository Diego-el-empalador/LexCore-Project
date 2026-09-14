# Flujo Completo de Análisis

```
1. view/paginas/cargar_contrato.py
   └── llama a: pipeline.analizar_contrato(texto, nombre)

2. controller/orquestador/pipeline.py
   ├── scala_bridge.tokenizar_contrato(texto, id, nombre)
   │   └── java -jar lexcore-scala.jar → JSON de cláusulas
   ├── prolog_bridge.validar_clausulas(clausulas)
   │   └── pyswip consulta clausula_riesgosa/3 → lista de hallazgos
   ├── estadisticas.calcular_estadisticas(clausulas, hallazgos)
   ├── lector_json.guardar_contrato_procesado(contrato)
   ├── lector_csv.guardar_hallazgos(id, hallazgos)
   └── lector_csv.guardar_auditoria(auditoria)

3. view/paginas/resultados.py
   └── lee st.session_state["ultimo_resultado"] y muestra hallazgos
```
