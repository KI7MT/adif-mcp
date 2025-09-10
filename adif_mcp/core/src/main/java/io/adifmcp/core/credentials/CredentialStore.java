package io.adifmcp.core.credentials;

import java.util.Optional;

/**
 * API for storing and retrieving credentials.
 */
public interface CredentialStore {

    void save(CredentialRecord record);

    Optional<CredentialRecord> find(String persona, String providerId);

    void delete(String persona, String providerId);
}
