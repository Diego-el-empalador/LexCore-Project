# Controlador principal encargado de la lógica y flujo de datos de LexCore
import subprocess
import json
import tempfile
from pathlib import Path
from controller.utils.config import SCALA_JAR
from controller.utils.logger import get_logger

logger = get_logger(__name__)


def _build_jar_if_missing(jar_path: Path) -> None:
    scala_dir = jar_path.parent.parent.parent
    if jar_path.exists():
        return
    logger.info(f"JAR de Scala no encontrado en {jar_path}, ejecutando 'sbt assembly' en {scala_dir}")
    proc = subprocess.run(
        ["sbt", "assembly"],
        cwd=str(scala_dir),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        logger.error("Fallo al compilar el JAR de Scala")
        logger.error(proc.stdout)
        logger.error(proc.stderr)
        raise RuntimeError(f"No se pudo construir el JAR de Scala: {proc.stderr}")


def tokenizar_contrato(texto: str, contrato_id: str, nombre: str) -> dict:
    _build_jar_if_missing(SCALA_JAR)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            temp_path = tmp.name

        resultado = subprocess.run(
            ["java", "-jar", str(SCALA_JAR), contrato_id, nombre, temp_path],
            input=texto,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if resultado.returncode != 0:
            logger.error(f"Scala error: {resultado.stderr}")
            raise RuntimeError(f"Error en Scala: {resultado.stderr}")

        stdout = resultado.stdout or ""
        stderr = resultado.stderr or ""
        payload_text = ""

        if temp_path:
            try:
                p = Path(temp_path)
                if p.exists():
                    payload_text = p.read_text(encoding="utf-8").strip()
            except Exception:
                payload_text = ""

        if not payload_text:
            payload_text = stdout.strip()

        if not payload_text:
            logger.error("Scala no devolvió JSON (ni por archivo ni por stdout)")
            if stderr.strip():
                logger.error(stderr)
            raise RuntimeError(
                "Scala no devolvio JSON. Recompila el JAR (sbt assembly) y vuelve a ejecutar Streamlit."
            )

        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError:
            logger.error("Salida de Scala no es JSON válido")
            logger.error(payload_text)
            raise

        if payload is None:
            raise RuntimeError("Scala devolvio 'null' en lugar de un objeto JSON con las clausulas.")
        if not isinstance(payload, dict):
            raise RuntimeError(f"Scala devolvio un JSON inesperado de tipo {type(payload).__name__}.")
        return payload
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass
