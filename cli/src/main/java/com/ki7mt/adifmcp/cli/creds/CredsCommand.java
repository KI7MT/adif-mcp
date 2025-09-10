package com.ki7mt.adifmcp.cli.creds;

import picocli.CommandLine.Command;

/**
 * Parent command for credential operations.
 */
@Command(
        name = "creds",
        description = "Manage credentials (set, get, list, delete, doctor).",
        subcommands = {
            SetCmd.class, GetCmd.class, ListCmd.class, DeleteCmd.class, DoctorCmd.class
        },
        mixinStandardHelpOptions = true
)
public class CredsCommand implements Runnable {

    @Override
    public void run() {
        // Picocli will show help when no subcommand is provided.
    }
}
