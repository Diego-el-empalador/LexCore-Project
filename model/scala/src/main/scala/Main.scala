import tokenizer.ContractParser
import java.nio.charset.StandardCharsets
import java.nio.file.{Files, Paths}

object Main:
  def main(args: Array[String]): Unit =
    val texto    = scala.io.Source.stdin.mkString
    val id       = if args.length > 0 then args(0) else "contrato_001"
    val nombre   = if args.length > 1 then args(1) else "Contrato"
    val contrato = ContractParser.parsear(id, nombre, texto)
    val json = ContractParser.toJson(contrato)
    if args.length > 2 then
      Files.write(Paths.get(args(2)), json.getBytes(StandardCharsets.UTF_8))
    else
      println(json)
