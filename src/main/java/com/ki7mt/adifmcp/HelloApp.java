package com.ki7mt.adifmcp;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.stage.Stage;

/** Minimal JavaFX window to prove wiring. */
public class HelloApp extends Application {

  @Override
  public void start(Stage stage) {
    stage.setTitle("ADIF-MCP");
    stage.setScene(new Scene(new Label("Hello from JavaFX 👋"), 320, 160));
    stage.show();
  }

  /** Safe launcher from a subcommand. */
  public static void launchUi() {
    Application.launch(HelloApp.class);
  }
}
