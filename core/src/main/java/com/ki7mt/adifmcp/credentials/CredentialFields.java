package com.ki7mt.adifmcp.credentials;

import java.util.Optional;

/**
 * Typed helpers for common credential shapes.
 */
public final class CredentialFields {

    private CredentialFields() {
    }

    /**
     * Username + password pair.
     */
    public record UserPass(String username, String password) {

    }

    /**
     * Username + API key pair.
     */
    public record ApiKey(String username, String apiKey) {

    }

    public static Optional<UserPass> asUserPass(CredentialRecord r) {
        var u = r.fields().get("username");
        var p = r.fields().get("password");
        return (u != null && p != null) ? Optional.of(new UserPass(u, p)) : Optional.empty();
    }

    public static Optional<ApiKey> asApiKey(CredentialRecord r) {
        var u = r.fields().get("username");
        var k = r.fields().get("api_key");
        return (u != null && k != null) ? Optional.of(new ApiKey(u, k)) : Optional.empty();
    }
}
