# Integración Python → Prolog

## Mecanismo
Python usa la librería `pyswip` para comunicarse con SWI-Prolog en proceso.

## Flujo
```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult("model/prolog/base_conocimiento/hechos.pl")
prolog.consult("model/prolog/base_conocimiento/reglas_generales.pl")

# Afirmar cláusulas dinámicamente
prolog.assertz("clausula(1, penalidad, 'multa del 10% mensual')")

# Consultar riesgos
for sol in prolog.query("clausula_riesgosa(Id, Tipo, Severidad)"):
    print(sol)  # {'Id': 1, 'Tipo': b'penalidad', 'Severidad': b'alto'}
```

## Archivos Prolog cargados en orden
1. `hechos.pl` — define `clausula/3` como dinámico
2. `reglas_generales.pl` — reglas base de riesgo
3. `reglas_laborales.pl` / `reglas_civiles.pl` / `reglas_comerciales.pl` — según tipo
4. `validar_clausula.pl` — punto de entrada de consulta
