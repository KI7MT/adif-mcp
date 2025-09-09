package com.ki7mt.adifmcp.ui;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.stage.Stage;

public class HelloApp extends Application {

    @Override
    public void start(Stage stage) {
        stage.setTitle("adif-mcp");
        stage.setScene(new Scene(new Label("Hello from JavaFX 👋"), 320, 160));
        stage.show();
    }

    public static void launchUi() {
        Application.launch(HelloApp.class);
    }
}
