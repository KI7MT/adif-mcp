plugins {
    id("java")
    id("application")
    id("org.openjfx.javafxplugin") version "0.1.0"
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
    applicationDefaultJvmArgs = listOf("-Dadifmcp.version=${project.version}")
}

tasks.test { useJUnitPlatform() }

// TASK: Set runUi alias
tasks.register<JavaExec>("runUi") {
    group = "application"
    description = "Run the JavaFX UI"
    mainClass.set(application.mainClass)
    classpath = sourceSets["main"].runtimeClasspath
    args("ui")
}

// TASK: Publish JavaDocs docs/javadoc
tasks.register<Copy>("publishJavadoc") {
    dependsOn(tasks.javadoc)
    from(tasks.javadoc)
    into(layout.projectDirectory.dir("docs/javadoc"))
}
