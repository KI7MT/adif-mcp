rootProject.name = "adif-mcp"

include("core")
include("cli")
include("ui")
include("server")
include("providers:provider-clublog")
include("providers:provider-eqsl")
include("providers:provider-lotw")
include("providers:provider-qrz")


pluginManagement {
    repositories { mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { mavenCentral() }
}
