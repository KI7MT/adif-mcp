package com.ki7mt.adifmcp.cli.creds;

import java.nio.file.Path;

import com.ki7mt.adifmcp.cli.Ssot;
import com.ki7mt.adifmcp.credentials.CredentialStore;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.ExecutionException;
import picocli.CommandLine.Option;

@Command(name = "doctor", description = "Check credential backend health.")
public class DoctorCmd implements Runnable {

    @Option(names = "--ssot")
    Path ssot;

    @Override
    public void run() {
        var root = Ssot.resolve(ssot);
        try (var store = CredentialStore.open(root)) {
            System.out.println(store.doctor());
        } catch (Exception e) {
            throw new ExecutionException(new CommandLine(this), "Doctor failed: " + e.getMessage(), e);
        }
    }
}
