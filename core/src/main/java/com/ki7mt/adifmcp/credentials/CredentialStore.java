package com.ki7mt.adifmcp.credentials;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;

/**
 * Facade for credential access. Chooses an active backend.
 */
public final class CredentialStore implements AutoCloseable {

    /**
     * Env var to provide passphrase for portable backend.
     */
    public static final String ENV_PASSPHRASE = "ADIF_MCP_CREDS_PASSPHRASE";

    private final StoreBackend backend;

    private CredentialStore(StoreBackend backend) {
        this.backend = backend;
    }

    /**
     * Open a store rooted at the SSOT path.
     */
    public static CredentialStore open(Path ssotRoot) {
        // v1: start with portable file backend only (OS keychain later)
        var portable = new com.ki7mt.adifmcp.credentials.backends.PortableFileBackend(ssotRoot);
        return new CredentialStore(portable);
    }

    public void put(CredentialRecord record) throws IOException {
        backend.put(record);
    }

    public Optional<CredentialRecord> get(String persona, String provider) throws IOException {
        return backend.get(persona, provider);
    }

    public List<CredentialRecord> list() throws IOException {
        return backend.list();
    }

    public boolean delete(String persona, String provider) throws IOException {
        return backend.delete(persona, provider);
    }

    public String doctor() {
        return backend.doctor();
    }

    @Override
    public void close() throws IOException {
        backend.close();
    }
}
