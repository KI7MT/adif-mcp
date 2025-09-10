plugins {
  id("java-library")
}

dependencies {
  implementation(project(":core"))
  implementation(project(":sync"))

  // Choose this later on: HTTP stack later (Javalin, Undertow, etc.)
  // implementation("io.javalin:javalin:6.3.0")

  testImplementation("org.junit.jupiter:junit-jupiter:5.10.3")
}
