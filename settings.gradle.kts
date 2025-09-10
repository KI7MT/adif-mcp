// settings.gradle.kts

pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
        // If you later need snapshots, uncomment:
        // maven("https://s01.oss.sonatype.org/content/repositories/snapshots/")
    }
}

rootProject.name = "adif-mcp"

// Logical module names
include("spi", "core", "cli", "sync", "server")

// Map modules to physical directories under adif_mcp/
project(":spi").projectDir    = file("adif_mcp/spi")
project(":core").projectDir   = file("adif_mcp/core")
project(":cli").projectDir    = file("adif_mcp/cli")
project(":sync").projectDir   = file("adif_mcp/sync")
project(":server").projectDir = file("adif_mcp/server")
