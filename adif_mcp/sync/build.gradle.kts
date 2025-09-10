plugins {
  id("java-library")
}

dependencies {
  implementation(project(":core"))
  // Sync orchestrator logic depends on core (and transitively spi)
  testImplementation("org.junit.jupiter:junit-jupiter:5.10.3")
}
