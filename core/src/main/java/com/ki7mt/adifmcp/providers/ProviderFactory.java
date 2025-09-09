package com.ki7mt.adifmcp.providers;

public interface ProviderFactory {

    String id();                 // e.g., "eqsl"

    String apiVersion();         // e.g., "1.0"

    ProviderClient create(ProviderContext ctx, ProviderCredentials creds);
}
