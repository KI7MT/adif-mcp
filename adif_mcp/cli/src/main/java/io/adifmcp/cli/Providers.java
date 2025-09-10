package io.adifmcp.cli;

import picocli.CommandLine.Command;

@Command(name = "providers", description = "List installed providers")
public class Providers implements Runnable {

    @Override
    public void run() {
        System.out.println("Installed providers:");
        System.out.println(" (none)");
    }
}
