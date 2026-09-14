# Manejo de Errores entre Módulos

## Error: JAR de Scala no encontrado
- Causa: no se compiló con `sbt assembly`.
- Dónde: `scala_bridge.py` lanza `FileNotFoundError`.
- Solución: ejecutar `cd model/scala && sbt assembly`.

## Error: SWI-Prolog no instalado
- Causa: `pyswip` no encuentra el binario de Prolog.
- Dónde: `prolog_bridge.py` lanza error al importar `pyswip`.
- Solución: instalar SWI-Prolog y agregar al PATH del sistema.

## Error: archivo de datos corrupto
- Causa: CSV o JSON modificado manualmente con formato incorrecto.
- Dónde: `lector_csv.py` o `lector_json.py` lanza `ValueError` o `JSONDecodeError`.
- Solución: eliminar el archivo afectado; se recreará vacío en el siguiente análisis.

## Error: texto de contrato vacío
- Causa: el usuario no ingresó texto.
- Dónde: `cargar_contrato.py` valida antes de llamar al pipeline.
- Solución: el frontend muestra un `st.warning` sin propagar el error.
