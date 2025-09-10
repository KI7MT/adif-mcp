// Root build.gradle.kts  — root is a java-platform (BOM) project
import org.gradle.jvm.tasks.Jar
import org.gradle.api.tasks.javadoc.Javadoc
import org.gradle.external.javadoc.StandardJavadocDocletOptions

// Root build.gradle.kts
group = "io.adifmcp"
group = "io.adifmcp"
version = providers.gradleProperty("version").getOrElse("0.4.0-SNAPSHOT")

plugins {
    id("java-platform")
}

javaPlatform {
    allowDependencies()
}

dependencies {
    constraints {
        api("info.picocli:picocli:4.7.6")
        api("com.fasterxml.jackson.core:jackson-annotations:2.17.2")
        api("com.fasterxml.jackson.core:jackson-databind:2.17.2")
    }
}

subprojects {
    plugins.withType<JavaPlugin> {
        // Java plugin available → safe to configure
        the<JavaPluginExtension>().apply {
            toolchain { languageVersion.set(JavaLanguageVersion.of(21)) }
            withSourcesJar()
            withJavadocJar()
        }

        tasks.withType<JavaCompile>().configureEach {
            options.encoding = "UTF-8"
            options.release.set(21)
        }

        tasks.withType<Javadoc>().configureEach {
            (options as StandardJavadocDocletOptions).addStringOption("Xdoclint:none", "-quiet")
            options.encoding = "UTF-8"
        }

        tasks.withType<Test>().configureEach {
            useJUnitPlatform()
        }
    }

    configurations.all {
        resolutionStrategy.cacheChangingModulesFor(0, "seconds")
    }
}

subprojects {
    group = rootProject.group
    version = rootProject.version
}

subprojects {
  tasks.withType<Jar>().configureEach {
    manifest {
      attributes(
        "Implementation-Title" to project.name,
        "Implementation-Version" to project.version
      )
    }
  }
}

/**
 * Aggregate Javadoc across all Java subprojects.
 */
tasks.register<Javadoc>("javadocAll") {
    description = "Aggregate Javadoc across all modules"
    group = JavaBasePlugin.DOCUMENTATION_GROUP

    val allSources = files()
    val allClasspaths = files()

    subprojects.forEach { sub ->
        sub.plugins.withId("java") {
            val javaExt = sub.extensions.getByType(org.gradle.api.plugins.JavaPluginExtension::class.java)
            val main = javaExt.sourceSets.getByName("main")
            allSources.from(main.allJava)
            allClasspaths.from(main.compileClasspath)
        }
    }

    setSource(allSources)
    classpath = allClasspaths

    @Suppress("DEPRECATION")
    destinationDir = file("$buildDir/docs/javadoc-all")
    // If you prefer using layout, use the next line instead of the one above:
    // @Suppress("DEPRECATION")
    // destinationDir = layout.buildDirectory.dir("docs/javadoc-all").get().asFile

    (options as StandardJavadocDocletOptions).apply {
        addStringOption("Xdoclint:none", "-quiet")
        encoding = "UTF-8"
    }
}

// root build.gradle.kts
tasks.register<Copy>("publishJavadoc") {
    dependsOn("javadocAll")
    from(layout.buildDirectory.dir("docs/javadoc-all"))
    into(layout.projectDirectory.dir("docs/javadoc"))
}
tasks.named("build").configure { dependsOn("publishJavadoc") }
