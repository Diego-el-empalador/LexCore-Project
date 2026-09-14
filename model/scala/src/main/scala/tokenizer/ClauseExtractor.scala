package tokenizer

import models.{Clause, Token}
import scala.util.matching.Regex

object ClauseExtractor:
  private val tiposClausula = Map(
    "obligacion"       -> List("debe", "obligado", "responsable", "cumplir", "honorarios", "sin costo adicional", "remuneracion"),
    "plazo"            -> List("días", "dias", "meses", "año", "fecha", "plazo", "vencimiento", "dias habiles", "ciento veinte", "120"),
    "penalidad"        -> List("multa", "penalidad", "sanción", "sancion", "incumplimiento", "descuento", "retencion", "50%"),
    "confidencialidad" -> List("confidencial", "secreto", "privado", "divulgar"),
    "rescision"        -> List("rescindir", "terminar", "finalizar", "disolver", "resolver"),
    "no_competencia"   -> List("no competencia", "competidor", "competencia", "exclusividad"),
    "propiedad_intelectual" -> List("propiedad intelectual", "copyright", "codigo fuente", "licencia", "marca"),
    "datos_personales" -> List("datos personales", "biometric", "consentimiento", "privacidad", "tratamiento"),
    "arbitraje"        -> List("arbitraje", "laudo", "centro arbitral", "tribunal arbitral"),
    "modificacion_unilateral" -> List("unilateralmente", "modificar", "a sola decision", "a su sola discrecion")
  )

  private val marcadorClausula: Regex =
    """(?im)^\s*(cl[áa]usula|art[íi]culo|secci[óo]n|cap[íi]tulo|anexo|numeral|literal|condici[óo]n|primera|segunda|tercera|cuarta|quinta|sexta|septima|séptima|octava|novena|d[ée]cima|und[ée]cima|duod[ée]cima)\s*([ivxlcdm]+|\d+|[a-z])?[\.\:\-\)]?\s*""".r

  private val numeracionSimple: Regex =
    """(?im)^\s*([ivxlcdm]+|\d+|[a-z])[\.\)\-:]\s+""".r

  def extraer(texto: String, tokens: List[Token]): List[Clause] =
    val partes = segmentar(texto)
    partes.zipWithIndex.map { case (seg, idx) =>
      val textoClausula = seg.trim
      val tipo         = detectarTipo(textoClausula)
      val subpartes    = extraerPartes(textoClausula)
      val puntaje      = calcularPuntaje(textoClausula, tipo)
      Clause(idx + 1, tipo, textoClausula, subpartes, puntaje)
    }

  private def segmentar(texto: String): List[String] =
    val normalizado = texto
      .replaceAll("(?im)(?=^\\s*(cl[áa]usula|art[íi]culo|secci[óo]n|cap[íi]tulo|anexo|numeral|literal|condici[óo]n|primera|segunda|tercera|cuarta|quinta|sexta|septima|séptima|octava|novena|d[ée]cima|und[ée]cima|duod[ée]cima)\\b)", "\n###SEP### ")
      .replaceAll("(?im)(?=^\\s*([ivxlcdm]+|\\d+|[a-z])[\\.)\\-:]\\s+)", "\n###SEP### ")

    val segmentos = normalizado
      .split("###SEP###")
      .toList
      .map(_.trim)
      .filter(_.nonEmpty)

    if segmentos.size > 1 then segmentos
    else
      texto
        .split("""(?<=[\.\n])\s{1,}(?=(cl[áa]usula|art[íi]culo|secci[óo]n|cap[íi]tulo|anexo|numeral|literal|condici[óo]n|primera|segunda|tercera|cuarta|quinta|sexta|septima|séptima|octava|novena|d[ée]cima|und[ée]cima|duod[ée]cima|[ivxlcdm]+[\.)\-:]|\d+[\.)\-:]|[a-z][\.)]))""")
        .toList
        .map(_.trim)
        .filter(_.nonEmpty)

  private def extraerPartes(texto: String): List[String] =
    texto
      .split("[,:;\\n]+")
      .toList
      .map(_.trim)
      .filter(_.nonEmpty)

  private def detectarTipo(texto: String): String =
    val lower = texto.toLowerCase
    tiposClausula
      .find { case (_, palabras) => palabras.exists(lower.contains) }
      .map(_._1)
      .getOrElse("general")

  private def calcularPuntaje(texto: String, tipo: String): Int =
    val palabras = texto
      .split("\\W+")
      .toList
      .map(_.toLowerCase)
      .filter(_.nonEmpty)

    val palabrasClave = tiposClausula.values.toList.flatMap(identity)
    val coincidenciasTipo = tiposClausula
      .getOrElse(tipo, List.empty)
      .count(palabras.contains)

    val coincidenciasGenerales = palabras.count(palabrasClave.contains)
    val longitud = palabras.length

    val base = coincidenciasTipo * 2 + coincidenciasGenerales
    val escala = if longitud > 0 then math.min(10, base + longitud / 20) else 0
    math.max(0, escala)
