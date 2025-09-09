package com.ki7mt.adifmcp;

import com.ki7mt.adifmcp.cli.Serve;
import com.ki7mt.adifmcp.cli.Ui;
import picocli.CommandLine;
import picocli.CommandLine.Command;

@Command(name = "adif-mcp", description = "ADIF MCP CLI", mixinStandardHelpOptions = true)
public class Main implements Runnable {
    @Override public void run() { CommandLine.usage(this, System.out); }

    public static void main(String[] args) {
        CommandLine root = new CommandLine(new Main());
        root.addSubcommand("ui", new Ui());
        root.addSubcommand("serve", new Serve());
        int code = root.execute(args);
        System.exit(code);
    }
}
