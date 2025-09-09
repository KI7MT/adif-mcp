rootProject.name = "adif-mcp"

include("core")
include("cli")
include("ui")
include("server")
include("providers:provider-eqsl")


pluginManagement {
    repositories { mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { mavenCentral() }
}
