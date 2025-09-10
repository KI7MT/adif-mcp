package io.adifmcp.cli;

import picocli.CommandLine.Command;

@Command(name = "serve", description = "Start local MCP HTTP server (stub)")
public class Serve implements Runnable {

    @Override
    public void run() {
        System.out.println("Server stub (not implemented yet).");
    }
}
