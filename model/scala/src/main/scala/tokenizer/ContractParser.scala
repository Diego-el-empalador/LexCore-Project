package tokenizer

import models.{Contract, Clause}
import utils.TextNormalizer
import ujson.*

object ContractParser:
  def parsear(id: String, nombre: String, texto: String): Contract =
    val textoNorm = TextNormalizer.normalizar(texto)
    val tokens    = Tokenizer.tokenizar(textoNorm)
    val clausulas = ClauseExtractor.extraer(textoNorm, tokens)
    Contract(id, nombre, texto, clausulas)

  def calcularRiesgoInicial(clausulas: List[Clause]): Int =
    if clausulas.isEmpty then 0
    else clausulas.map(_.riesgoInicial).sum / clausulas.size

  def toJson(contrato: Contract): String =
    val json = ujson.Obj(
      "contrato_id"   -> contrato.id,
      "nombre"        -> contrato.nombre,
      "riesgo_inicial"-> calcularRiesgoInicial(contrato.clausulas),
      "clausulas"     -> contrato.clausulas.map { c =>
        ujson.Obj(
          "id"            -> c.id,
          "tipo"          -> c.tipo,
          "texto"         -> c.texto,
          "partes"        -> ujson.Arr.from(c.partes),
          "riesgo_inicial"-> c.riesgoInicial
        )
      }
    )
    ujson.write(json, indent = 2)
