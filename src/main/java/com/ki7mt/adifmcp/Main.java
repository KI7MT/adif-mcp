package com.ki7mt.adifmcp;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Model.CommandSpec;
import picocli.CommandLine.Spec;

@Command(
    name = "adif-mcp",
    description = "ADIF MCP — CLI & UI launcher",
    mixinStandardHelpOptions = true, // adds --help, --version
    versionProvider = Main.VersionProvider.class,
    subcommands = {Chat.class, Ui.class})
public class Main implements Runnable {

  @Spec CommandSpec spec;

  @Override
  public void run() {
    // Default action when no subcommand is provided
    spec.commandLine().usage(System.out);
  }

  public static void main(String[] args) {
    int code = new CommandLine(new Main()).execute(args);
    System.exit(code);
  }

  /** Supplies version text for --version (kept simple for now). */
  static class VersionProvider implements CommandLine.IVersionProvider {
    @Override
    public String[] getVersion() {
      return new String[] {"adif-mcp 0.4.0-SNAPSHOT (Java 21)", "Copyright (c) KI7MT"};
    }
  }
}
