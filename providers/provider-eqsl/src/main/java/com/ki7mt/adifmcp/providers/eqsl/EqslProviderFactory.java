package com.ki7mt.adifmcp.providers.eqsl;

import com.ki7mt.adifmcp.providers.ProviderClient;
import com.ki7mt.adifmcp.providers.ProviderContext;
import com.ki7mt.adifmcp.providers.ProviderCredentials;
import com.ki7mt.adifmcp.providers.ProviderFactory;

public final class EqslProviderFactory implements ProviderFactory {

    @Override
    public String id() {
        return "eqsl";
    }

    @Override
    public String apiVersion() {
        return "1.0";
    }

    @Override
    public ProviderClient create(ProviderContext ctx, ProviderCredentials creds) {
        return new EqslClient(ctx, creds);
    }
}
