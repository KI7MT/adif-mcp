package io.adifmcp.core.credentials;

import java.nio.file.Path;

/**
 * Factory for opening credential stores.
 */
public final class CredentialStores {

    private CredentialStores() {
        // utility class
    }

    /**
     * Open the default credential store for the given SSOT root.
     *
     * @param ssotRoot SSOT root directory
     * @return a credential store (currently in-memory; file backend to follow)
     */
    public static CredentialStore open(Path ssotRoot) {
        return new InMemoryCredentialStore();
    }
}
