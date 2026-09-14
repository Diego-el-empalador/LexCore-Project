package tokenizer

import models.Token

object Tokenizer:
  private val palabrasLegales = Set(
    "obligación", "obligacion", "plazo", "penalidad", "multa",
    "rescisión", "rescision", "confidencial", "contrato", "cláusula"
  )

  def tokenizar(texto: String): List[Token] =
    texto
      .split("\\s+")
      .zipWithIndex
      .map { case (palabra, idx) =>
        Token(idx, palabra, clasificar(palabra))
      }
      .toList

  private def clasificar(palabra: String): String =
    if palabrasLegales.contains(palabra.toLowerCase) then "legal" else "comun"
