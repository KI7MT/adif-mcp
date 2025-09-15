import org.gradle.jvm.tasks.Jar
import org.gradle.language.jvm.tasks.ProcessResources

plugins {
    id("application")
}

dependencies {
    implementation(project(":core"))
    implementation("info.picocli:picocli:4.7.6")
}

application {
    mainClass.set("io.adifmcp.cli.Main")
}

// Ensure the CLI jar has Implementation-Title/Version
tasks.named<Jar>("jar") {
    manifest {
        attributes(
            "Implementation-Title" to "adif-mcp",
            "Implementation-Version" to project.version
        )
    }
}

// (Optional) fallback for IDE/gradle :run when no jar manifest is present
tasks.processResources {
    val ver = project.version.toString()
    inputs.property("appVersion", ver)
    filesMatching("build-info.properties") {
        expand("appVersion" to ver)
    }
}

tasks.named<ProcessResources>("processResources") {
    inputs.property("version", project.version)
    filesMatching("build-info.properties") {
        expand("version" to project.version.toString())
    }
}
