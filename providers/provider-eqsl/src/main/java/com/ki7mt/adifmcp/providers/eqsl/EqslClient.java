package com.ki7mt.adifmcp.providers.eqsl;

import java.time.Instant;
import java.util.Optional;

import com.ki7mt.adifmcp.providers.AuthStatus;
import com.ki7mt.adifmcp.providers.FetchOptions;
import com.ki7mt.adifmcp.providers.FetchResult;
import com.ki7mt.adifmcp.providers.Health;
import com.ki7mt.adifmcp.providers.ProviderClient;
import com.ki7mt.adifmcp.providers.ProviderContext;
import com.ki7mt.adifmcp.providers.ProviderCredentials;
import com.ki7mt.adifmcp.providers.RateLimit;
import com.ki7mt.adifmcp.providers.UserPassCredentials;

public final class EqslClient implements ProviderClient {

    private final ProviderContext ctx;
    private final ProviderCredentials creds;

    public EqslClient(ProviderContext ctx, ProviderCredentials creds) {
        this.ctx = ctx;
        this.creds = creds;
    }

    @Override
    public Health ping() {
        return new Health(true, "eqsl stub");
    }

    @Override
    public AuthStatus authCheck() {
        if (creds instanceof UserPassCredentials up
                && up.username() != null && !up.username().isBlank()
                && up.password() != null && !up.password().isBlank()) {
            return AuthStatus.OK;
        }
        return AuthStatus.MISSING;
    }

    @Override
    public FetchResult fetchSince(Instant since, FetchOptions opt) {
        // stub: return empty; wire real HTTP later
        return FetchResult.empty();
    }

    @Override
    public Optional<RateLimit> rateLimitInfo() {
        return Optional.empty();
    }

    @Override
    public void close() {
        /* no-op */ }
}
