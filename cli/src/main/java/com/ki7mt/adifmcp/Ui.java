package com.ki7mt.adifmcp;

import picocli.CommandLine.Command;

@Command(
        name = "ui",
        description = "Launch the JavaFX UI (if available on the classpath).",
        mixinStandardHelpOptions = true)
public class Ui implements Runnable {

    @Override
    public void run() {
        try {
            Class<?> app = Class.forName("com.ki7mt.adifmcp.ui.HelloApp");
            app.getMethod("launchUi").invoke(null);
        } catch (ClassNotFoundException e) {
            System.err.println(
                    "UI is not on the CLI classpath.\n"
                    + "Run the UI with: ./gradlew :ui:run\n"
                    + "or use the packaged UI launcher.");
            System.exit(2);
        } catch (Throwable t) {
            t.printStackTrace();
            System.exit(1);
        }
    }
}
