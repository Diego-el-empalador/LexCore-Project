# Integración Python → Scala

## Mecanismo
Python invoca el JAR compilado de Scala vía `subprocess.run`.

## Comando
```python
subprocess.run(
    ["java", "-jar", "model/scala/target/scala-3.3.1/lexcore-scala.jar", contrato_id, nombre],
    input=texto_contrato,   # stdin
    capture_output=True,
    text=True,
    encoding="utf-8"
)
```

## Entrada
Texto plano del contrato enviado por `stdin`.

## Salida
JSON en `stdout` con la estructura:
```json
{
  "contrato_id": "abc123",
  "nombre": "Contrato de Servicios",
  "clausulas": [
    { "id": 1, "tipo": "obligacion", "texto": "...", "partes": [] }
  ]
}
```

## Compilar el JAR
```bash
cd model/scala
sbt assembly
```
