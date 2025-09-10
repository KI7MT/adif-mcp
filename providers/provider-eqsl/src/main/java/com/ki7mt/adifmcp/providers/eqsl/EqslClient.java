package com.ki7mt.adifmcp.providers.eqsl;

import com.ki7mt.adifmcp.credentials.CredentialFields;
import com.ki7mt.adifmcp.credentials.CredentialStore;
import com.ki7mt.adifmcp.providers.AuthStatus;
import com.ki7mt.adifmcp.providers.ProviderClient;
import com.ki7mt.adifmcp.providers.ProviderContext;
import com.ki7mt.adifmcp.providers.ProviderCredentials;

import java.nio.file.Path;

/**
 * Minimal eQSL provider client that validates presence/shape of credentials.
 * Network I/O is deliberately out of scope for this step.
 */
public final class EqslClient implements ProviderClient {

    private final ProviderContext ctx;
    private final ProviderCredentials creds;

    public EqslClient(ProviderContext ctx, ProviderCredentials creds) {
        this.ctx = ctx;
        this.creds = creds;
    }

    @Override
    public String id() {
        return "eqsl";
    }

    @Override
    public String apiVersion() {
        return "1.0";
    }

    @Override
    public AuthStatus authCheck(String persona, Path ssotRoot) {
        try (var store = CredentialStore.open(ssotRoot)) {
            var recOpt = store.get(persona, "eqsl");
            if (recOpt.isEmpty()) {
                return AuthStatus.MISSING;
            }

            var up = CredentialFields.asUserPass(recOpt.get());
            if (up.isEmpty()) {
                return AuthStatus.MISSING;
            }

            var u = up.get().username();
            var p = up.get().password();
            if (u == null || u.isBlank() || p == null || p.isBlank()) {
                return AuthStatus.MISSING;
            }

            return AuthStatus.OK;
        } catch (Exception e) {
            return AuthStatus.INVALID;
        }
    }
}
