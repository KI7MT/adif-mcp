plugins { id("application") }

dependencies {
    implementation(project(":core"))
    // e.g. implementation("io.javalin:javalin:6.3.0") later
}

application {
    mainClass.set("com.ki7mt.adifmcp.server.ServerMain")
}
