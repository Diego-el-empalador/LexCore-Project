package models

case class Contract(id: String, nombre: String, textoOriginal: String, clausulas: List[Clause])
