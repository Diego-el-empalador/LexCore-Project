package utils

object TextNormalizer:
  def normalizar(texto: String): String =
    texto
      .trim
      .replaceAll("[\\r\\n]+", "\n")
      .replaceAll("[\\t\\x0B\\f ]+", " ")
