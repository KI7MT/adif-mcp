plugins {
    id("application")
    id("org.openjfx.javafxplugin") version "0.1.0"
}

dependencies {
    implementation(project(":core"))
}

javafx {
    version = "21.0.4"
    modules = listOf("javafx.controls") // pulls base/graphics/controls with correct platform classifiers
}

application {
    mainClass.set("com.ki7mt.adifmcp.ui.HelloApp")
}
