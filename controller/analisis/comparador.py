import pandas as pd
from controller.almacenamiento.lector_csv import leer_auditorias
from controller.utils.logger import get_logger

logger = get_logger(__name__)

def comparar_contratos(id1: str, id2: str) -> dict:
    df = leer_auditorias()

    def buscar(cid: str) -> dict:
        fila = df[df["contrato_id"] == cid]
        return fila.iloc[0].to_dict() if not fila.empty else {}

    return {"contrato_1": buscar(id1), "contrato_2": buscar(id2)}
