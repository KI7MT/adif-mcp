package io.adifmcp.spi;

import java.util.Map;

/**
 * Opaque, already-decrypted fields for a provider (e.g., username, password,
 * apiKey).
 */
public record ProviderCredentials(Map<String, String> fields) {

    public String get(String key) {
        return fields.get(key);
    }
}
