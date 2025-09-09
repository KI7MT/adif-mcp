package com.ki7mt.adifmcp.providers;

/**
 * Defines a factory interface for creating {@code ProviderClient} instances.
 *
 * The {@code ProviderFactory} interface provides methods to retrieve metadata
 * about a provider and to create instances of {@code ProviderClient} for managing
 * interactions with the provider. Implementing classes are responsible for
 * providing the core logic required to initialize and configure clients.
 *
 * This interface supports the following functionalities:
 * - Retrieve the identifier of the provider.
 * - Retrieve the API version supported by the provider.
 * - Create a new {@code ProviderClient} instance using the provided context and credentials.
 *
 * Methods:
 * - {@code id()}: Returns a string that represents the unique identifier of the provider.
 * - {@code apiVersion()}: Returns the supported version of the provider's API.
 * - {@code create(ProviderContext ctx, ProviderCredentials creds)}: Creates a new
 *   {@code ProviderClient} instance configured with the specified context and credentials.
 */
public interface ProviderFactory {

    String id();                 // e.g., "eqsl"

    String apiVersion();         // e.g., "1.0"

    ProviderClient create(ProviderContext ctx, ProviderCredentials creds);
}
