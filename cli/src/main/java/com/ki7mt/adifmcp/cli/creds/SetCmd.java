package com.ki7mt.adifmcp.cli.creds;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

import com.ki7mt.adifmcp.credentials.CredentialRecord;
import com.ki7mt.adifmcp.credentials.CredentialStore;

import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

/**
 * Set credentials for a persona/provider.
 */
@Command(name = "set", description = "Set credentials for a persona/provider.")
public class SetCmd implements Runnable {

    @Parameters(index = "0", paramLabel = "PERSONA")
    String persona;
    @Parameters(index = "1", paramLabel = "PROVIDER")
    String provider;

    @Option(names = "--username")
    String username;
    @Option(names = "--password")
    String password;
    @Option(names = "--api-key")
    String apiKey;

    @Option(names = "--ssot", description = "SSOT root (defaults to ADIF_MCP_HOME or ~/.adif-mcp)")
    Path ssot;

    @Override
    public void run() {
        Path root = Ssot.resolve(ssot);
        Map<String, String> fields = new HashMap<>();
        if (username != null) {
            fields.put("username", username);
        }
        if (password != null) {
            fields.put("password", password);
        }
        if (apiKey != null) {
            fields.put("api_key", apiKey);
        }

        var rec = new CredentialRecord(persona, provider, fields);
        try (var store = CredentialStore.open(root)) {
            store.put(rec);
            System.out.printf("Saved credentials for %s/%s%n", persona, provider);
        } catch (Exception e) {
            throw new RuntimeException("Failed to save credentials: " + e.getMessage(), e);
        }
    }
}
