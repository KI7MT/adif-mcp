plugins { id("application") }

dependencies {
    implementation(project(":core"))
    implementation("info.picocli:picocli:4.7.6")
    annotationProcessor("info.picocli:picocli-codegen:4.7.6")
    // testImplementation("org.junit.jupiter:junit-jupiter:5.10.3")
}

application {
    mainClass.set("com.ki7mt.adifmcp.Main")
    applicationDefaultJvmArgs = listOf("-Dadifmcp.version=${project.version}")
}
