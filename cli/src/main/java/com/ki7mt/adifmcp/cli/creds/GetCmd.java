package com.ki7mt.adifmcp.cli.creds;

import java.nio.file.Path;

import com.ki7mt.adifmcp.cli.Ssot;
import com.ki7mt.adifmcp.credentials.CredentialStore;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.ExecutionException;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

@Command(name = "get", description = "Get credentials for a persona/provider.")
public class GetCmd implements Runnable {

    @Parameters(index = "0")
    String persona;
    @Parameters(index = "1")
    String provider;

    @Option(names = "--show", description = "Show secret values")
    boolean show;
    @Option(names = "--ssot")
    Path ssot;

    @Override
    public void run() {
        Path root = Ssot.resolve(ssot);
        try (var store = CredentialStore.open(root)) {
            var rec = store.get(persona, provider).orElse(null);
            if (rec == null) {
                System.out.println("No credentials found.");
                return;
            }
            System.out.printf("persona=%s provider=%s%n", rec.persona(), rec.provider());
            rec.fields().forEach((k, v) -> {
                if (!show && ("password".equals(k) || "api_key".equals(k))) {
                    System.out.printf("  %s=****%n", k);
                } else {
                    System.out.printf("  %s=%s%n", k, v);
                }
            });
        } catch (Exception e) {
            throw new ExecutionException(new CommandLine(this), "Failed to get credentials: " + e.getMessage(), e);
        }
    }
}
