plugins {
    // no plugins at root
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
