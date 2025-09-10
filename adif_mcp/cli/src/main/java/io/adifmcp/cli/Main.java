package io.adifmcp.cli;

import picocli.CommandLine;
import picocli.CommandLine.Command;

@Command(name = "adif-mcp", description = "ADIF MCP CLI", mixinStandardHelpOptions = true)
public class Main implements Runnable {

    @Override
    public void run() {
        new CommandLine(this).usage(System.out);
    }

    public static void main(String[] args) {
        CommandLine root = new CommandLine(new Main());
        root.addSubcommand("providers", new Providers());
        root.addSubcommand("serve", new Serve());
        System.exit(root.execute(args));
    }
}
