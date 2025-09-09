package com.ki7mt.adifmcp;

import com.ki7mt.adifmcp.cli.Serve;

import picocli.CommandLine;
import picocli.CommandLine.Command;

/**
 * The {@code Main} class serves as the entry point for the ADIF MCP command-line interface (CLI)
 * application. It uses the Picocli library to handle command parsing, execution, and help generation.
 * <p>
 * This class is annotated with the {@code @Command} annotation, defining the top-level name and
 * description of the CLI application. It also specifies that standard help options, such as
 * {@code --help} and {@code --version}, are included.
 * <p>
 * The {@code Main} class implements the {@link Runnable} interface, which is required for execution
 * within the Picocli framework. When executed, the application displays help text listing the
 * available subcommands and their descriptions.
 * <p>
 * Key features:
 * - Defines the main CLI application for the ADIF MCP project.
 * - Registers subcommands for specific operations, including:
 *   - "ui": Launches the JavaFX-based UI (see {@code Ui} class).
 *   - "serve": Starts a local HTTP server stub (see {@code Serve} class).
 *   - "providers": Lists installed provider implementations (see {@code Providers} class).
 * - Manages the lifecycle of the application, passing execution to the appropriate subcommand
 *   based on the user's input.
 * <p>
 * Subcommands:
 * - {@code "ui"}: Launches the JavaFX UI for the application.
 * - {@code "serve"}: Initiates a local HTTP server (functionality not implemented yet).
 * - {@code "providers"}: Displays a list of installed providers available in the system.
 * <p>
 * Error handling:
 * - The CLI exits with the corresponding code upon normal or exceptional termination:
 *   - 0: Successful execution.
 *   - Any other code indicates an error scenario.
 * <p>
 * Entry point:
 * The class contains a {@code main} method, serving as the application's entry point when executed
 * from the command line. It creates an instance of {@link CommandLine}, adds subcommands, and
 * invokes the execution logic based on the provided arguments.
 */
@Command(
        name = "adif-mcp",
        description = "ADIF MCP CLI",
        mixinStandardHelpOptions = true)
public class Main implements Runnable {

    @Override
    public void run() {
        CommandLine.usage(this, System.out);
    }

    public static void main(String[] args) {
        CommandLine root = new CommandLine(new Main());
        root.addSubcommand("ui", new Ui());
        root.addSubcommand("serve", new Serve());
        root.addSubcommand("providers", new com.ki7mt.adifmcp.cli.Providers());
        int code = root.execute(args);
        System.exit(code);
    }
}
