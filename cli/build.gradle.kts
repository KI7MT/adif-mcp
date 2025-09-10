plugins { id("application") }

dependencies {
    implementation(project(":core"))
    implementation("info.picocli:picocli:4.7.6")
    implementation(project(":providers:provider-eqsl"))
    implementation(project(":ui"))
}

application {
    mainClass.set("com.ki7mt.adifmcp.Main")
    applicationDefaultJvmArgs = listOf("-Dadifmcp.version=${project.version}")
}
