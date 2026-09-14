name         := "lexcore-scala"
version      := "0.1.0-SNAPSHOT"
scalaVersion := "3.3.1"

libraryDependencies += "com.lihaoyi" %% "ujson" % "3.1.3"

assembly / mainClass       := Some("Main")
assembly / assemblyJarName := "lexcore-scala.jar"

assembly / assemblyMergeStrategy := {
  case PathList("META-INF", _*) => MergeStrategy.discard
  case _                        => MergeStrategy.first
}
