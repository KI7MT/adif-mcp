package io.adifmcp.core.credentials;

import java.util.Map;

/**
 * Represents a credential entry for a persona + provider combination.
 *
 * @param persona Persona ID (e.g., "KI7MT")
 * @param providerId Provider key (e.g., "eqsl")
 * @param fields Arbitrary key/value credential fields (username, password, API
 * key, etc.)
 */
public record CredentialRecord(
        String persona,
        String providerId,
        Map<String, String> fields
        ) {

}
