package com.ki7mt.adifmcp.cli.providers;

import picocli.CommandLine.Command;

/**
 * Subcommands for per-provider health checks.
 */
@Command(
        name = "doctor",
        description = "Provider health checks (credentials, basic readiness).",
        subcommands = {
            DoctorEqsl.class
        // DoctorQrz.class  (add later)
        },
        mixinStandardHelpOptions = true
)
public class ProvidersDoctor implements Runnable {

    @Override
    public void run() {
        /* shows help */ }
}
