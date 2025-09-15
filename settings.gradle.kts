// settings.gradle.kts  — keep this minimal
rootProject.name = "adif-mcp"

include("spi","core","cli","sync","server")

project(":spi").projectDir    = file("adif_mcp/spi")
project(":core").projectDir   = file("adif_mcp/core")
project(":cli").projectDir    = file("adif_mcp/cli")
project(":sync").projectDir   = file("adif_mcp/sync")
project(":server").projectDir = file("adif_mcp/server")

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
    }
}
