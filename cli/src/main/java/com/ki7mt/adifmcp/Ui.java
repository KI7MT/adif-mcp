package com.ki7mt.adifmcp;

import picocli.CommandLine.Command;

/**
 * The {@code Ui} class serves as a command-line subcommand for launching
 * the JavaFX-based user interface of the application. It is intended to be
 * executed within the context of a command-line interface (CLI) framework
 * implemented using the Picocli library.
 * <p>
 * Features:
 * - Attempts to locate and invoke the `HelloApp` class from the package
 *   {@code com.ki7mt.adifmcp.ui}.
 * - Calls the `launchUi` method on the `HelloApp` class to initiate the UI.
 * <p>
 * Error Handling:
 * - If the `HelloApp` class cannot be found on the classpath, an error message
 *   is displayed, explaining how to run the UI using Gradle or a packaged UI
 *   launcher. The process exits with code 2.
 * - If any other exception occurs during the invocation of the UI, a stack trace
 *   is printed to the standard error stream, and the process exits with code 1.
 * <p>
 * Usage:
 * This class should be registered as a subcommand in the Picocli CLI application,
 * under the name `ui`. It is typically invoked via the command line by users who
 * wish to launch the graphical user interface for the application.
 * <p>
 * Lifecycle:
 * - On execution, the `run` method is called, which performs the logic to
 *   locate and launch the JavaFX-based UI.
 * <p>
 * Dependencies:
 * - The UI functionality requires the presence of the `HelloApp` class on the
 *   application's classpath.
 */
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
                    """
                            UI is not on the CLI classpath.
                            Run the UI with: ./gradlew :ui:run
                            or use the packaged UI launcher.""");
            System.exit(2);
        } catch (Throwable t) {
            //noinspection CallToPrintStackTrace
            t.printStackTrace();
            System.exit(1);
        }
    }
}
