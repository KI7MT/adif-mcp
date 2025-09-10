plugins { id("application") }

dependencies {
    implementation(project(":core"))
    implementation(project(":providers:provider-eqsl"))
    implementation("info.picocli:picocli:4.7.6")
    implementation(project(":ui"))
}

application {
    mainClass.set("com.ki7mt.adifmcp.Main")
    applicationDefaultJvmArgs = listOf("-Dadifmcp.version=${project.version}")
}
