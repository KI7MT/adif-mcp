package com.ki7mt.adifmcp.cli;

import picocli.CommandLine.Command;

@Command(
        name = "providers",
        description = "List installed providers and run provider utilities.",
        subcommands = {
            com.ki7mt.adifmcp.cli.providers.ProvidersDoctor.class
        },
        mixinStandardHelpOptions = true
)
public class Providers implements Runnable {

    @Override
    public void run() {
        // existing logic: list installed providers via ServiceLoader
        // (leave as-is)
    }
}
