package com.ki7mt.adifmcp.providers;

/**
 * Represents API key-based credentials for authentication with a provider.
 *
 * The {@code ApiKeyCredentials} record is an immutable implementation of the
 * {@code ProviderCredentials} interface. It encapsulates authentication details
 * required to access provider services that rely on API key and username
 * mechanisms.
 *
 * This record contains:
 * - A username, which identifies the user or account.
 * - An API key, which serves as the authentication token for the provider.
 *
 * The {@code ApiKeyCredentials} can be used to authenticate requests made
 * through a {@code ProviderClient} implementation. It provides a simple
 * and secure way to supply authentication details for providers supporting
 * API key-based authentication.
 */
public record ApiKeyCredentials(String username, String apiKey) implements ProviderCredentials {

}
