package com.ki7mt.adifmcp;

import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(
    name = "chat",
    description = "Chat with your local ADIF data (placeholder).",
    mixinStandardHelpOptions = true)
public class Chat implements Runnable {

  @Option(
      names = {"-q", "--query"},
      description = "Question to ask.",
      arity = "0..1")
  String query;

  @Override
  public void run() {
    if (query == null || query.isBlank()) {
      System.out.println(
          "chat> (placeholder) Try: adif-mcp chat --query \"How many QSOs last month?\"");
    } else {
      // placeholder behavior
      System.out.println("chat> You asked: " + query);
      System.out.println("chat> (stub) Hook up provider/state reads here.");
    }
  }
}
