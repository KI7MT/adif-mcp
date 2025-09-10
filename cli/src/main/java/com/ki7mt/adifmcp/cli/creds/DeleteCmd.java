package com.ki7mt.adifmcp.cli.creds;

import java.nio.file.Path;

import com.ki7mt.adifmcp.cli.Ssot;
import com.ki7mt.adifmcp.credentials.CredentialStore;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.ExecutionException;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

@Command(name = "delete", description = "Delete credentials for a persona/provider.")
public class DeleteCmd implements Runnable {

    @Parameters(index = "0")
    String persona;
    @Parameters(index = "1")
    String provider;
    @Option(names = "--ssot")
    Path ssot;

    @Override
    public void run() {
        var root = Ssot.resolve(ssot);
        try (var store = CredentialStore.open(root)) {
            boolean ok = store.delete(persona, provider);
            System.out.println(ok ? "Deleted." : "Not found.");
        } catch (Exception e) {
            throw new ExecutionException(new CommandLine(this), "Failed to delete credentials: " + e.getMessage(), e);
        }
    }
}
