package io.adifmcp.spi;

/**
 * Service-loaded entrypoint to construct clients.
 */
public interface ProviderFactory {

    /**
     * Stable provider id, e.g. "eqsl", "qrz". Must match client.id().
     */
    String id();

    /**
     * Create a ready-to-use client. No network calls inside the constructor.
     */
    ProviderClient create(ProviderContext context, ProviderCredentials credentials);
}
