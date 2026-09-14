# model/python — Módulo de Modelado de Dominio (Fabiana Castro)

## Jerarquía de clases

```
Clausula  (clase base)
├── ClausulaLaboral
├── ClausulaArrendamiento
├── ClausulaServicios
└── ClausulaCompraventa

fabricar_clausula()  → función fábrica (Factory Method)

Contrato
└── cargar_desde_scala()  → integración con Scala + Prolog
    └── usa fabricar_clausula() para instanciar subclases

Dictamen
└── recibe Contrato + estadisticas → genera score y nivel de riesgo
```

## Conceptos del sílabo demostrados

| Archivo | Concepto |
|---|---|
| `clausula.py` | Herencia, polimorfismo (evaluar()), atributos de clase, Factory Method |
| `contrato.py` | Composición, agregación (Contrato tiene Lista[Clausula]), encapsulamiento |
| `analizador.py` | Uso de pandas (DataFrame, value_counts) y numpy (array, mean, std, max) |

## Integración con el pipeline

```
pipeline.py
  ↓ tokenizar_contrato()   →  Scala (tokenización NLP)
  ↓ validar_clausulas()    →  Prolog (lógica de reglas)
  ↓ Contrato.cargar_desde_scala()
      └─ fabricar_clausula()  →  instancia subclase según categoría
  ↓ calcular_perfil_estadistico()  →  análisis con pandas/numpy
  ↓ Dictamen.resumen()     →  score 0-100, nivel, recomendación
```

El módulo actúa como **capa de modelo** entre los bridges de Scala/Prolog
y la vista de Streamlit, manteniendo la arquitectura MVC del proyecto.
