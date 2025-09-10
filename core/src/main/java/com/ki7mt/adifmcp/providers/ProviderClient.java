package com.ki7mt.adifmcp.providers;

import java.nio.file.Path;

/**
 * Common interface for all provider clients (minimal v0).
 */
public interface ProviderClient {

    /**
     * Unique provider ID, e.g. "eqsl", "qrz".
     */
    String id();

    /**
     * API version string (optional).
     */
    default String apiVersion() {
        return "1.0";
    }

    /**
     * Validate that credentials for the given persona are usable. No network
     * I/O; just presence/shape checks.
     */
    AuthStatus authCheck(String persona, Path ssotRoot);
}
