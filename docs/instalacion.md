# Instalación de LexCore

## Requisitos previos

| Herramienta   | Versión mínima | Descarga                          |
|---------------|----------------|-----------------------------------|
| Python        | 3.11           | https://python.org                |
| Java (JDK)    | 11             | https://adoptium.net              |
| sbt           | 1.9            | https://www.scala-sbt.org         |
| SWI-Prolog    | 9.x            | https://www.swi-prolog.org        |

## Pasos

```bash
# 1. Clonar el repositorio
git clone <url-repo>
cd LexCore

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. Compilar el módulo Scala
cd model/scala
sbt assembly
cd ../..

# 4. Ejecutar la aplicación
streamlit run view/app.py
```
