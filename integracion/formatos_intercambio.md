# Formatos de Intercambio de Datos

## JSON de cláusulas (Scala → Python)
```json
{
  "contrato_id": "a1b2c3d4",
  "nombre": "Contrato de Arrendamiento",
  "clausulas": [
    {
      "id": 1,
      "tipo": "plazo",
      "texto": "El contrato tendrá vigencia de 12 meses",
      "partes": []
    }
  ]
}
```

## Hecho Prolog (Python → Prolog, vía assertz)
```prolog
clausula(1, plazo, 'El contrato tendrá vigencia de 12 meses').
```

## Resultado de consulta Prolog (Prolog → Python)
```python
{"Id": 1, "Tipo": b"plazo", "Severidad": b"medio"}
```

## Hallazgo normalizado (Python interno)
```python
{"clausula_id": 1, "tipo_riesgo": "plazo", "severidad": "medio"}
```
