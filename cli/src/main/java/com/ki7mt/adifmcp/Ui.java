package com.ki7mt.adifmcp;

import picocli.CommandLine.Command;

/**
 * The {@code Ui} class serves as a CLI subcommand for launching the JavaFX-based user interface
 * (UI) of the application. It is intended to be executed as part of the command-line interface.
 *
 * This class is designed to dynamically invoke the launch method of the JavaFX UI application
 * (`HelloApp`), provided it is available on the runtime classpath. If the application is not
 * present or any other exception occurs during execution, appropriate error messages are
 * displayed to inform the user.
 *
 * The {@code Ui} command is registered as a subcommand of the main CLI application. It relies on
 * the `picocli.CommandLine` library for command execution and option parsing.
 *
 * Key features:
 * - Dynamically loads the JavaFX UI class and invokes its entry point method.
 * - Provides error handling for cases where the UI is not available on the classpath or an
 *   unexpected error occurs during runtime.
 * - Outputs descriptive error or guidance messages to the console for better user experience.
 *
 * Command name: {@code ui}
 * Command description: Launch the JavaFX UI (if available on the classpath).
 * Implements: {@link Runnable}, making it suitable for execution within the CLI framework.
 */
@Command(
        name = "ui",
        description = "Launch the JavaFX UI (if available on the classpath).",
        mixinStandardHelpOptions = true)
public class Ui implements Runnable {

    /**
     * Executes the CLI subcommand to launch the JavaFX-based user interface (UI) for the application.
     *
     * The method attempts to dynamically load the UI class defined as `com.ki7mt.adifmcp.ui.HelloApp`
     * and invoke its static method `launchUi`. If the required UI class is not found on the classpath,
     * it outputs an error message and terminates the application with an exit code of 2. If any other
     * exceptions occur during execution, the stack trace is printed, and the application terminates
     * with an exit code of 1.
     *
     * Key operations:
     * - Dynamically loads the `HelloApp` class from the specified package.
     * - Invokes the `launchUi` method of the `HelloApp` class.
     * - Handles `ClassNotFoundException` by displaying appropriate error messages suggesting
     *   how to run the UI.
     * - Handles general exceptions by printing their stack trace and terminating the program.
     *
     * Exit codes:
     * - 0: Successful execution (implicit based on the application's expected flow).
     * - 1: Unexpected error occurred during execution (stack trace printed).
     * - 2: UI class not found on the classpath.
     */
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
