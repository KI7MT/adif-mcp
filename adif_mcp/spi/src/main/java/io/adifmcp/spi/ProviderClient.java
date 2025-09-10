package io.adifmcp.spi;

import java.time.Instant;
import java.util.Optional;

/**
 * Contract a provider must implement. No network side-effects on authCheck().
 */
public interface ProviderClient extends AutoCloseable {

    /**
     * Stable provider id, e.g. "eqsl", "qrz".
     */
    String id();

    /**
     * Optional API version string. Default "1.0".
     */
    default String apiVersion() {
        return "1.0";
    }

    /**
     * Validate credentials presence/shape only. No network I/O here.
     */
    AuthStatus authCheck(String personaId, java.nio.file.Path ssotRoot);

    /**
     * Fetch ADIF since the given time (inclusive). Network call.
     */
    FetchResult fetchSince(Instant since, FetchOptions options);

    /**
     * Optional rate-limit hints.
     */
    default Optional<RateLimit> rateLimitInfo() {
        return Optional.empty();
    }

    /**
     * Clean up any resources (HTTP client, etc.).
     */
    @Override
    void close();
}
