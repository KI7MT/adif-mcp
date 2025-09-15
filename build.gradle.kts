import org.gradle.jvm.tasks.Jar
import org.gradle.external.javadoc.StandardJavadocDocletOptions
import org.gradle.api.tasks.javadoc.Javadoc


// build.gradle.kts  — root
plugins {
    id("base")
}

group = "io.adifmcp"
version = providers.gradleProperty("version").getOrElse("0.4.0-SNAPSHOT")

subprojects {
    group = rootProject.group
    version = rootProject.version

    plugins.apply("java-library")

    extensions.configure(org.gradle.api.plugins.JavaPluginExtension::class.java) {
        toolchain.languageVersion.set(JavaLanguageVersion.of(21))
        withSourcesJar()
        withJavadocJar()
    }

    tasks.withType<org.gradle.api.tasks.compile.JavaCompile>().configureEach {
        options.encoding = "UTF-8"
        options.release.set(21)
    }

    tasks.withType<Javadoc>().configureEach {
        (options as StandardJavadocDocletOptions).apply {
            addStringOption("Xdoclint:none", "-quiet")
            encoding = "UTF-8"
        }
    }

    tasks.withType<Jar>().configureEach {
        manifest {
            attributes(
                "Implementation-Title" to project.name,
                "Implementation-Version" to project.version
            )
        }
    }
}

// Aggregate per-module javadoc -> build/docs/javadoc-all/<module>/
tasks.register<Sync>("javadocAll") {
    description = "Collect Javadoc from all modules into build/docs/javadoc-all"
    group = JavaBasePlugin.DOCUMENTATION_GROUP
    outputs.upToDateWhen { false }

    dependsOn(subprojects.map { it.tasks.matching { t -> t.name == "javadoc" } })

    subprojects.forEach { sub ->
        from(sub.layout.buildDirectory.dir("docs/javadoc")) { into(sub.name) }
    }
    into(layout.buildDirectory.dir("docs/javadoc-all"))
}

// Copy aggregate into docs/javadoc WITHOUT deleting existing files (wrappers)
tasks.register<Copy>("publishJavadoc") {
    description = "Copy aggregated Javadoc into docs/javadoc (non-destructive)"
    group = JavaBasePlugin.DOCUMENTATION_GROUP
    outputs.upToDateWhen { false }

    dependsOn("javadocAll")
    from(layout.buildDirectory.dir("docs/javadoc-all"))
    into(layout.projectDirectory.dir("docs/javadoc"))
    // keep existing files; just overwrite matching ones
    duplicatesStrategy = DuplicatesStrategy.INCLUDE
}
