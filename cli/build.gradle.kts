plugins { id("application") }

dependencies {
    implementation(project(":core"))
    implementation("info.picocli:picocli:4.7.6")
    implementation(project(":providers:provider-eqsl"))
}

application {
    mainClass.set("com.ki7mt.adifmcp.Main")
    applicationDefaultJvmArgs = listOf("-Dadifmcp.version=${project.version}")
}
