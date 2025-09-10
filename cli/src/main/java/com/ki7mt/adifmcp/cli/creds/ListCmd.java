package com.ki7mt.adifmcp.cli.creds;

import java.nio.file.Path;

import com.ki7mt.adifmcp.credentials.CredentialStore;

import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "list", description = "List all stored credentials (persona/provider pairs).")
public class ListCmd implements Runnable {

    @Option(names = "--ssot")
    Path ssot;

    @Override
    public void run() {
        var root = Ssot.resolve(ssot);
        try (var store = CredentialStore.open(root)) {
            var items = store.list();
            if (items.isEmpty()) {
                System.out.println("(none)");
            } else {
                items.forEach(r -> System.out.printf("%s/%s%n", r.persona(), r.provider()));
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to list credentials: " + e.getMessage(), e);
        }
    }
}
