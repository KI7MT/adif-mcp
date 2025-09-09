package com.ki7mt.adifmcp.cli;

import java.util.ServiceLoader;

import com.ki7mt.adifmcp.providers.ProviderFactory;

import picocli.CommandLine.Command;

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
