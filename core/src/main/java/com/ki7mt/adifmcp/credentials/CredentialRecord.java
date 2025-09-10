package com.ki7mt.adifmcp.credentials;

import java.util.Collections;
import java.util.Map;

/**
 * A credential value object for a (persona, provider) pair. Stores opaque
 * string fields (e.g., username, password, api_key).
 */
public final class CredentialRecord {

    private final String persona;
    private final String provider;
    private final Map<String, String> fields; // secrets included

    public CredentialRecord(String persona, String provider, Map<String, String> fields) {
        this.persona = persona;
        this.provider = provider;
        this.fields = fields == null ? Map.of() : Map.copyOf(fields);
    }

    /**
     * Persona/callsign scope (e.g., "KI7MT").
     */
    public String persona() {
        return persona;
    }

    /**
     * Provider id (e.g., "eqsl", "qrz").
     */
    public String provider() {
        return provider;
    }

    /**
     * Immutable view of all fields.
     */
    public Map<String, String> fields() {
        return Collections.unmodifiableMap(fields);
    }

    /**
     * Returns a field value or null if absent.
     */
    public String get(String key) {
        return fields.get(key);
    }

    /**
     * Convenience; throws if missing.
     */
    public String require(String key) {
        String v = get(key);
        if (v == null || v.isBlank()) {
            throw new IllegalStateException("Missing field: " + key);
        }
        return v;
    }
}
