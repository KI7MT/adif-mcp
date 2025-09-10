package io.adifmcp.spi;

/**
 * Result of a credential sanity check (no network).
 */
public enum AuthStatus {
    OK, // credentials present & shaped correctly
    MISSING, // not found for persona/provider
    INVALID      // wrong shape/empty fields
}
