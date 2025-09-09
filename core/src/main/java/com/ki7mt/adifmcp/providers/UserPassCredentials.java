package com.ki7mt.adifmcp.providers;

/**
 * Represents username and password-based credentials for authentication with a provider.
 *
 * The {@code UserPassCredentials} record is an immutable implementation of the
 * {@code ProviderCredentials} interface. It encapsulates authentication details
 * required to access provider services that rely on username and password mechanisms.
 *
 * This record contains:
 * - A username, which identifies the user or account.
 * - A password, which serves as the authentication secret for the user.
 *
 * The {@code UserPassCredentials} can be used to authenticate requests made
 * through a {@code ProviderClient} implementation. It provides a straightforward
 * and secure method to supply login credentials for providers supporting
 * username-password authentication.
 */
public record UserPassCredentials(String username, String password) implements ProviderCredentials {

}
