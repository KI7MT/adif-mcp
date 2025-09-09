package com.ki7mt.adifmcp.providers;

import java.time.Instant;
import java.util.Optional;

/**
 * Represents a client interface for interacting with a data provider.
 *
 * The {@code ProviderClient} interface defines methods for performing essential
 * operations against a data provider, such as checking the provider's health,
 * verifying authentication status, fetching data, and retrieving rate limit
 * information. It extends {@code AutoCloseable} to support resource cleanup when
 * the client is no longer needed.
 */
public interface ProviderClient extends AutoCloseable {

    Health checkHealth();

    AuthStatus checkAuth();

    Health ping();

    AuthStatus authCheck();

    FetchResult fetchSince(Instant since, FetchOptions opt);

    Optional<RateLimit> rateLimit();

    Optional<RateLimit> rateLimitInfo();

    @Override
    void close();
}
