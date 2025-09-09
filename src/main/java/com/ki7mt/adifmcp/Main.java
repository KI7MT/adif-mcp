package com.ki7mt.adifmcp;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Model.CommandSpec;
import picocli.CommandLine.Spec;

@Command(
    name = "adif-mcp",
    description = "ADIF MCP — CLI & UI launcher",
    mixinStandardHelpOptions = true, // --help, --version
    versionProvider = Main.VersionProvider.class,
    subcommands = {Chat.class, Ui.class})
public class Main implements Runnable {

  @Spec CommandSpec spec;

  @Override
  public void run() {
    // default action: show usage
    spec.commandLine().usage(System.out);
  }

  public static void main(String[] args) {
    int code = new CommandLine(new Main()).execute(args);
    System.exit(code);
  }

    static class VersionProvider implements CommandLine.IVersionProvider {
        @Override
        public String[] getVersion() {
            return new String[] {
                    "adif-mcp 0.4.0-SNAPSHOT",
                    "Copyright (c) KI7MT"
            };
        }
    }
}
