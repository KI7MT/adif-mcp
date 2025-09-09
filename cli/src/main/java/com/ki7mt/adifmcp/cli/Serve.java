package com.ki7mt.adifmcp.cli;

import picocli.CommandLine.Command;

@Command(
        name = "serve",
        description = "Start the local MCP HTTP server (stub).",
        mixinStandardHelpOptions = true)
public class Serve implements Runnable {
    @Override public void run() {
        System.out.println("Server stub: not implemented yet.");
    }
}
