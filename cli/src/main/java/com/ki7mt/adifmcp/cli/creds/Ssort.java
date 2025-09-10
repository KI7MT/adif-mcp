package com.ki7mt.adifmcp.cli.creds;

import java.nio.file.Path;

/**
 * Resolves SSOT root using ADIF_MCP_HOME or defaults to ~/.adif-mcp.
 */
final class Ssot {

    private Ssot() {
    }

    static Path resolve(Path override) {
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
