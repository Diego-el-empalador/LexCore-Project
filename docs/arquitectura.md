# Arquitectura del Sistema LexCore

## Patrón MVC

```
Usuario
  ↓
VIEW  (view/app.py + paginas/)          ← Streamlit
  ↓
CONTROLLER (controller/orquestador/)    ← Python
  ↙                  ↘
MODEL/scala          MODEL/prolog
(Scala 3, JAR)       (SWI-Prolog, pyswip)
  ↘                  ↙
MODEL/data (CSV / JSON)
```

## Flujo de una auditoría

1. El usuario carga el texto en `cargar_contrato.py`.
2. `pipeline.py` orquesta el análisis completo.
3. `scala_bridge.py` invoca el JAR con `subprocess`, recibe JSON de cláusulas.
4. `prolog_bridge.py` carga las reglas y consulta `clausula_riesgosa/3`.
5. `estadisticas.py` calcula métricas con pandas/numpy.
6. Los resultados se guardan en `model/data/` y se devuelven a la vista.
7. `resultados.py` muestra hallazgos con badges de color por severidad.

## Responsabilidades por capa

La arquitectura de LexCore separa las responsabilidades del sistema para facilitar su mantenimiento y evolución.

- **Vista:** permite la interacción del usuario con el sistema mediante Streamlit.
- **Controlador:** coordina el flujo de información entre la interfaz y los módulos de análisis.
- **Modelo Scala:** procesa y analiza las cláusulas obtenidas de los contratos.
- **Modelo Prolog:** aplica reglas lógicas para identificar posibles cláusulas riesgosas.
- **Datos:** almacena la información utilizada y generada durante el proceso de auditoría.

Esta separación permite mantener los componentes organizados y facilita la incorporación de nuevas funcionalidades.