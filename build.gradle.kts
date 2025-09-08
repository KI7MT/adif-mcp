plugins {
    id("java")
    id("application")
    id("org.openjfx.javafxplugin") version "0.1.0"
    id("com.diffplug.spotless") version "6.25.0"    // google format
    id("checkstyle")
    id("pmd")
    id("com.github.spotbugs") version "6.0.26"
}

spotless {
    java {
        googleJavaFormat("1.22.0")
        target("src/**/*.java")
    }
}

checkstyle {
    toolVersion = "10.17.0"
    // use the built-in Google checks or point to your own XML under config/checkstyle/checks.xml
    // config = resources.text.fromFile("config/checkstyle/checks.xml")
}

pmd {
    toolVersion = "7.4.0"
    ruleSets = listOf() // disable defaults
    ruleSetFiles = files("config/pmd/ruleset.xml") // optional custom rules
}

spotbugs {
    toolVersion.set("4.9.0")
    effort.set(com.github.spotbugs.snom.Effort.MAX)
    reportLevel.set(com.github.spotbugs.snom.Confidence.LOW)
}

group = "com.ki7mt"
version = "0.4.0-SNAPSHOT"

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(21)) }
}

dependencies {
    implementation("info.picocli:picocli:4.7.6")
    annotationProcessor("info.picocli:picocli-codegen:4.7.6")
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.2")
    implementation("com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:2.17.2")
    testImplementation(platform("org.junit:junit-bom:5.10.3"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

javafx {
    version = "21"
    modules = listOf("javafx.controls")
}

application {
    mainClass.set("com.ki7mt.adifmcp.Main")
}

tasks.test { useJUnitPlatform() }
