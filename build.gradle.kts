import org.gradle.api.tasks.Sync

plugins {
    id("java")
}

dependencies {
    implementation(project(":core"))
}

allprojects {
    group = "com.ki7mt"
    version = "0.4.0-SNAPSHOT"
}

subprojects {
    // Ensure the Java plugin is applied before configuring its extension
    apply(plugin = "java")

    // Configure Java toolchain & compiler for each subproject
    extensions.configure<JavaPluginExtension> {
        toolchain.languageVersion.set(JavaLanguageVersion.of(21))
    }

    tasks.withType<JavaCompile>().configureEach {
        options.encoding = "UTF-8"
        options.release.set(21)
    }

    tasks.withType<Test>().configureEach {
        useJUnitPlatform()
    }
}

// Root build.gradle.kts

// ... your existing allprojects {} and subprojects {} blocks above ...

// Aggregate Javadoc for all subprojects into docs/javadoc (single index.html)
tasks.register<Javadoc>("javadocAll") {
    description = "Generate aggregated Javadoc into docs/javadoc"
    group = JavaBasePlugin.DOCUMENTATION_GROUP

    // Collect 'main' source sets from all Java subprojects
    val mainSourceSets = subprojects.mapNotNull {
        it.extensions.findByType(JavaPluginExtension::class.java)?.sourceSets?.findByName("main")
    }

    // Sources: flatten to a single FileTree
    val allJavaTrees = mainSourceSets.map { it.allJava }
    source(allJavaTrees)                       // OK: SourceTask.source(...) accepts Iterable<FileTree>

    // Classpath: flatten to a single FileCollection
    val allClasspaths = mainSourceSets.map { it.compileClasspath }
    classpath = files(*allClasspaths.toTypedArray())

    // Output where MkDocs expects
    destinationDir = layout.projectDirectory.dir("docs/javadoc").asFile

    // Optional: don’t fail the whole build on Javadoc warnings
    (options as StandardJavadocDocletOptions).addBooleanOption("Xdoclint:none", true)
    isFailOnError = false
}
