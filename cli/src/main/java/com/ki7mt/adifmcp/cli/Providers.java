package com.ki7mt.adifmcp.cli;

import java.util.ServiceLoader;

import com.ki7mt.adifmcp.providers.ProviderFactory;

import picocli.CommandLine.Command;

/**
 * The {@code Providers} class serves as a CLI subcommand for listing all installed provider
 * implementations in the system. It is integrated into the command-line interface as part of a
 * larger application using the Picocli library.
 * <p>
 * The class dynamically loads all provider factory implementations available through the
 * {@link ServiceLoader} mechanism, displays their identifiers and API versions, and indicates
 * whether any providers are installed.
 * <p>
 * Command name: {@code providers}
 * Command description: List installed providers.
 * Implements: {@link Runnable}, allowing it to be executed within the CLI framework.
 * <p>
 * Key operations:
 * - Uses {@link ServiceLoader} to discover implementations of {@code ProviderFactory}.
 * - For each discovered factory, retrieves the provider's identifier and supported API version
 *   using the {@code id()} and {@code apiVersion()} methods, respectively.
 * - Outputs the list of installed providers to the standard output in a formatted manner.
 * - If no providers are found, it outputs "(none)" to indicate the absence of installed providers.
 */
@Command(
        name = "providers",
        description = "List installed providers",
        mixinStandardHelpOptions = true
)
public class Providers implements Runnable {

    @Override
    public void run() {
        var loader = ServiceLoader.load(ProviderFactory.class);
        System.out.println("Installed providers:");
        boolean any = false;
        for (ProviderFactory f : loader) {
            any = true;
            System.out.printf(" - %s (api %s)%n", f.id(), f.apiVersion());
        }
        if (!any) {
            System.out.println(" (none)");
        }
    }
}
