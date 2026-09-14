# LexCore

Sistema inteligente de auditoría legal de contratos con integración híbrida entre `Scala`, `Prolog`, `Python` y `Streamlit`.

## Descripción

LexCore analiza contratos en español, separa cláusulas, razona sobre riesgos legales y presenta resultados visuales orientados a auditoría preventiva. El sistema combina:

- `Scala` para tokenización y segmentación funcional de cláusulas.
- `Prolog` para razonamiento declarativo y detección de cláusulas abusivas.
- `Python` para orquestación del pipeline, analítica, fallbacks y persistencia.
- `Streamlit + Plotly` para visualización interactiva y operación por lotes.

## Tecnologías y aporte al sílabo

| Tecnología | Rol en LexCore | Competencia demostrada |
|---|---|---|
| `Scala 3` | Extracción y tokenización de cláusulas | Programación funcional y procesamiento de texto |
| `SWI-Prolog` | Reglas legales y detección de riesgos | Lógica declarativa y sistemas expertos |
| `Python 3.11+` | Pipeline, fallbacks, dataset, analítica | Integración, POO, manejo de datos |
| `pandas / numpy` | Métricas, anomalías, dataset de referencia | Ciencia de datos aplicada |
| `Streamlit` | Frontend de auditoría | Desarrollo rápido de interfaces |
| `Plotly` | Gráficos de riesgo y estadísticas | Visualización de información |
| `pdfplumber` | Extracción de texto desde PDF | Ingesta documental |

## Arquitectura

```text
view/         -> frontend Streamlit
controller/   -> orquestación, persistencia, análisis y reportes
model/python/ -> modelos de dominio y analítica
model/scala/  -> tokenizador / extractor funcional
model/prolog/ -> base de conocimiento y reglas legales
model/data/   -> dataset, historial y resultados
```

## Dataset usado

LexCore incluye un dataset de referencia en:

`model/data/conocimiento/dataset_contratos.csv`

Características:

- `240` registros realistas en español.
- Tipos de contrato: `laboral`, `arrendamiento`, `servicios`, `compraventa`.
- Columnas:
  - `contrato_id`
  - `tipo_contrato`
  - `texto_clausula`
  - `tipo_clausula`
  - `es_abusiva`
  - `severidad`
  - `articulo_violado`
  - `descripcion_riesgo`
  - `pais`

Uso en el sistema:

- Entrena frecuencias de palabras clave por tipo.
- Sirve como base comparativa para score y patrones.
- Alimenta la pantalla de estadísticas globales.

## Funcionalidades finales

- Análisis individual de contratos pegados o cargados como `.txt` / `.pdf`.
- Procesamiento masivo de múltiples contratos con barra de progreso.
- Fallback automático si falla Scala o Prolog.
- Soporte para textos largos mediante `chunking`.
- Reglas legales ampliadas para:
  - `no_competencia`
  - `propiedad_intelectual`
  - `datos_personales`
  - `arbitraje`
  - `modificacion_unilateral`
- Resultados visuales con:
  - gauge de score
  - severidades por color
  - dona de tipos de cláusula
  - comparativa contra dataset
  - anomalías estadísticas
- Historial paginado con filtros, recarga de detalle y eliminación.

## Instalación paso a paso

### 1. Requisitos previos

- `Python 3.11+`
- `Java 11+`
- `sbt`
- `SWI-Prolog`

### 2. Crear entorno virtual

```powershell
cd "C:\ruta\hacia\LexCore"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configurar SWI-Prolog en Windows

```powershell
$env:SWI_HOME_DIR="C:\Program Files\swipl"
$env:LIBSWIPL_PATH="C:\Program Files\swipl\bin\libswipl.dll"
$env:Path += ";C:\Program Files\swipl\bin"
```

### 4. Compilar Scala

Si `sbt` no está en `PATH`, usa la ruta completa:

```powershell
cd "C:\ruta\hacia\LexCore\model\scala"
& "C:\Program Files (x86)\sbt\bin\sbt.bat" assembly
```

O si ya está disponible:

```powershell
cd "C:\ruta\hacia\LexCore\model\scala"
sbt assembly
```

### 5. Ejecutar la app

```powershell
cd "C:\ruta\hacia\LexCore"
python -m streamlit run view/app.py
```

Luego abre:

- `http://localhost:8501`

## Uso

### Caso individual

1. Ir a `Cargar Contrato`.
2. Elegir tipo de contrato.
3. Pegar texto o subir `.txt/.pdf`.
4. Pulsar `Analizar contrato(s)`.
5. Revisar `Resultados`, `Historial` y `Estadísticas`.

### Caso masivo

1. Ir a `Cargar Contrato`.
2. Seleccionar `Subir archivos .txt/.pdf`.
3. Cargar varios contratos.
4. Ejecutar análisis del lote.
5. Descargar el `reporte comparativo CSV`.

## Capturas en texto

### Inicio

```text
[Logo SVG justicia]
LexCore
Contratos analizados | Score promedio | Tipo más frecuente | Registros referencia
```

### Cargar Contrato

```text
Tipo de contrato
Metodo de carga
Vista previa del texto
Caracteres / cláusulas estimadas
Barra de progreso por etapa
```

### Resultados

```text
Score de seguridad (gauge)
Severidades detectadas
Distribución de tipos
Hallazgos por cláusula
Comparación con dataset
Exportar JSON / TXT
```

### Estadísticas

```text
Evolución de scores
Top 5 cláusulas riesgosas
Heatmap de severidad por tipo
Distribución del dataset
```

### Historial

```text
Tabla paginada
Filtros por fecha y nivel
Ver detalle
Eliminar registro
```

## Problemas encontrados y solución aplicada

- `SWI-Prolog not found`
  - Se resolvió documentando variables de entorno para Windows.
- `Scala no devolvía stdout`
  - Se cambió el puente para leer JSON desde archivo temporal.
- `Textos largos / múltiples cláusulas`
  - Se añadió chunking en Python y fallback inteligente si Scala no separa bien.
- `CSV histórico inconsistente`
  - Se volvió tolerante la lectura con `pandas` usando `on_bad_lines="skip"`.
- `sbt instalado pero no reconocido`
  - Se documentó ejecución con ruta completa a `sbt.bat`.

## Créditos del equipo

Completa esta sección con los nombres reales del grupo:

| Integrante | Módulo / responsabilidad |
|---|---|
| `Diego`    | Frontend Streamlit / UX |
| `Nombre 2` | Pipeline Python / analítica |
| `Nombre 3` | Scala tokenizer |
| `Nombre 4` | Prolog / base de conocimiento |
| `Nombre 5` | Persistencia / dataset / documentación |

## Comandos útiles

```powershell
python -m streamlit run view/app.py
python -c "from controller.orquestador.pipeline import analizar_contrato; print('ok')"
```
## Equipo de Desarrollo
- Diego (Líder / Integración)