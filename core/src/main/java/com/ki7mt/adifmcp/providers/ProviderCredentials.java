package com.ki7mt.adifmcp.providers;

/**
 * Represents a sealed interface for provider credentials used in authentication.
 *
 * The {@code ProviderCredentials} interface serves as a common type for
 * different credential implementations that are used to authenticate with
 * provider clients. It defines a sealed hierarchy, allowing only specific
 * permitted classes to implement this interface.
 *
 * Permitted implementations include:
 * - {@code UserPassCredentials}: Represents username and password-based credentials.
 * - {@code ApiKeyCredentials}: Represents API key-based credentials.
 *
 * This interface is typically utilized by provider clients or factories that
 * require authentication details to interact with external services.
 */
public sealed interface ProviderCredentials permits UserPassCredentials, ApiKeyCredentials {
}
