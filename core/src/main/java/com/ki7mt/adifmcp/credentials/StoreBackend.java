package com.ki7mt.adifmcp.credentials;

import java.io.Closeable;
import java.io.IOException;
import java.util.List;
import java.util.Optional;

/**
 * Storage backend contract for credentials.
 */
public interface StoreBackend extends Closeable {

    void put(CredentialRecord record) throws IOException;

    Optional<CredentialRecord> get(String persona, String provider) throws IOException;

    List<CredentialRecord> list() throws IOException;

    boolean delete(String persona, String provider) throws IOException;

    /**
     * Basic self-test (e.g., roundtrip); return message describing the result.
     */
    String doctor();

    @Override
    default void close() throws IOException {
        /* no-op by default */ }
}
