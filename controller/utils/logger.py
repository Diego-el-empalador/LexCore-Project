import logging
from controller.utils.config import BASE_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "lexcore.log"),
        logging.StreamHandler(),
    ],
)

def get_logger(nombre: str) -> logging.Logger:
    return logging.getLogger(nombre)
