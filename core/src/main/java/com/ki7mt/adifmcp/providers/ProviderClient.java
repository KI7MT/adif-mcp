package com.ki7mt.adifmcp.providers;

import java.time.Instant;
import java.util.Optional;

public interface ProviderClient extends AutoCloseable {

    Health ping();

    AuthStatus authCheck();

    FetchResult fetchSince(Instant since, FetchOptions opt);

    Optional<RateLimit> rateLimitInfo();

    @Override
    void close();
}
