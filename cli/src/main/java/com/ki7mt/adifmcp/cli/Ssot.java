package com.ki7mt.adifmcp.cli;

import java.nio.file.Path;

public final class Ssot {

    private Ssot() {
    }

    public static Path resolve(Path override) {
        if (override != null) {
            return override.toAbsolutePath().normalize();
        }
        String env = System.getenv("ADIF_MCP_HOME");
        if (env != null && !env.isBlank()) {
            return Path.of(env).toAbsolutePath().normalize();
        }
        String userHome = System.getProperty("user.home");
        return Path.of(userHome, ".adif-mcp").toAbsolutePath().normalize();
    }
}
