package com.ki7mt.adifmcp;

import picocli.CommandLine.Command;

@Command(name = "ui", description = "Launch the JavaFX UI.", mixinStandardHelpOptions = true)
public class Ui implements Runnable {
  @Override
  public void run() {
    HelloApp.launchUi();
  }
}
