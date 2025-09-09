package com.ki7mt.adifmcp.providers;

import java.nio.file.Path;

/**
 * Represents the context required for creating and configuring provider clients.
 *
 * The ProviderContext record encapsulates essential information shared across
 * various providers. It includes the root directory path for interacting with
 * the provider's system of truth (SSOT). This path serves as a key reference
 * for storing or accessing data specific to the provider.
 *
 * The ProviderContext is typically used in factory methods for constructing
 * instances of {@code ProviderClient}.
 *
 * @param ssotRoot The root path to the provider's single source of truth (SSOT).
 */
public record ProviderContext(Path ssotRoot) {

}
