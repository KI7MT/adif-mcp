package com.ki7mt.adifmcp.cli.providers;

import java.nio.file.Path;
import java.util.ServiceLoader;

import com.ki7mt.adifmcp.cli.Ssot;
import com.ki7mt.adifmcp.providers.AuthStatus;
import com.ki7mt.adifmcp.providers.ProviderClient;
import com.ki7mt.adifmcp.providers.ProviderFactory;

import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

@Command(name = "eqsl", description = "Check eQSL credentials for a persona.")
public class DoctorEqsl implements Runnable {

    @Parameters(index = "0", paramLabel = "PERSONA", description = "Persona/callsign")
    String persona;

    @Option(names = "--ssot", description = "SSOT root (defaults to ADIF_MCP_HOME or ~/.adif-mcp)")
    Path ssot;

    @Override
    public void run() {
        Path root = Ssot.resolve(ssot);

        ProviderClient client = ServiceLoader.load(ProviderFactory.class).stream()
                .map(ServiceLoader.Provider::get)
                .filter(f -> "eqsl".equals(f.id()))
                .findFirst()
                .map(f -> f.create(/*ctx*/null, /*creds*/ null))
                .orElseThrow(() -> new IllegalStateException("eQSL provider not found on classpath"));

        AuthStatus st = client.authCheck(persona, root);
        System.out.println(st.name());

        if (st == AuthStatus.MISSING) {
            System.exit(2);
        }
        if (st == AuthStatus.INVALID) {
            System.exit(3);
        }
    }
}
