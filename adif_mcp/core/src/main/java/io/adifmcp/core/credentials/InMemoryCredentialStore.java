package io.adifmcp.core.credentials;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Simple in-memory credential store for testing/dev.
 */
public class InMemoryCredentialStore implements CredentialStore {

    private final Map<String, CredentialRecord> entries = new ConcurrentHashMap<>();

    @Override
    public void save(CredentialRecord record) {
        entries.put(key(record.persona(), record.providerId()), record);
    }

    @Override
    public Optional<CredentialRecord> find(String persona, String providerId) {
        return Optional.ofNullable(entries.get(key(persona, providerId)));
    }

    @Override
    public void delete(String persona, String providerId) {
        entries.remove(key(persona, providerId));
    }

    private static String key(String persona, String providerId) {
        return persona + "::" + providerId;
    }
}
