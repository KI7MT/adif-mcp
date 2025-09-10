package com.ki7mt.adifmcp.credentials.backends;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.ki7mt.adifmcp.credentials.CredentialRecord;
import com.ki7mt.adifmcp.credentials.StoreBackend;
import com.ki7mt.adifmcp.credentials.util.Crypto;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

import static java.nio.file.StandardOpenOption.*;

public final class PortableFileBackend implements StoreBackend {
    private static final ObjectMapper M = new ObjectMapper();
    private final Path credsFile;     // ${SSOT}/config/creds.enc.json
    private final char[] passphrase;  // from ADIF_MCP_CREDS_PASSPHRASE

    public PortableFileBackend(Path ssotRoot) {
        var cfgDir = ssotRoot.resolve("config");
        this.credsFile = cfgDir.resolve("creds.enc.json");
        var env = System.getenv("ADIF_MCP_CREDS_PASSPHRASE");
        if (env == null || env.isBlank()) {
            throw new IllegalStateException("ADIF_MCP_CREDS_PASSPHRASE not set (required for portable credentials backend).");
        }
        this.passphrase = env.toCharArray();
    }

    @Override public void put(CredentialRecord record) throws IOException {
        var list = readAll();
        // replace if exists
        var filtered = list.stream()
                .filter(r -> !(r.persona().equals(record.persona()) && r.provider().equals(record.provider())))
                .collect(Collectors.toCollection(ArrayList::new));
        filtered.add(record);
        writeAll(filtered);
    }

    @Override public Optional<CredentialRecord> get(String persona, String provider) throws IOException {
        return readAll().stream()
                .filter(r -> r.persona().equals(persona) && r.provider().equals(provider))
                .findFirst();
    }

    @Override public List<CredentialRecord> list() throws IOException {
        return readAll();
    }

    @Override public boolean delete(String persona, String provider) throws IOException {
        var list = readAll();
        var newList = list.stream()
                .filter(r -> !(r.persona().equals(persona) && r.provider().equals(provider)))
                .toList();
        if (newList.size() == list.size()) return false;
        writeAll(newList);
        return true;
    }

    @Override public String doctor() {
        try {
            // -> ensure dir exists
            Files.createDirectories(credsFile.getParent());
            // -> read (may be empty) and write back no-op
            writeAll(readAll());
            return "PortableFileBackend ok (" + credsFile + ")";
        } catch (Exception e) {
            return "PortableFileBackend error: " + e.getMessage();
        }
    }

    // ---------- internals ----------

    private List<CredentialRecord> readAll() throws IOException {
        if (!Files.exists(credsFile)) return List.of(); // fresh
        var envelope = M.readTree(Files.newBufferedReader(credsFile, StandardCharsets.UTF_8));
        if (!envelope.hasNonNull("v") || envelope.get("v").asInt() != 1)
            throw new IOException("Unsupported creds envelope version");
        var salt  = Crypto.unb64(envelope.get("salt").asText());
        var nonce = Crypto.unb64(envelope.get("nonce").asText());
        var ct    = Crypto.unb64(envelope.get("ct").asText());

        try {
            var key = Crypto.deriveKey(passphrase, salt);
            var plain = Crypto.decryptAesGcm(key, nonce, ct);
            var root = M.readTree(plain);
            if (root.get("version").asInt() != 1) throw new IOException("Unsupported creds data version");
            var arr = root.withArray("entries");
            var out = new ArrayList<CredentialRecord>(arr.size());
            for (var node : arr) {
                var persona  = node.get("persona").asText();
                var provider = node.get("provider").asText();
                var fieldsObj = node.with("fields");
                Map<String,String> fields = new HashMap<>();
                fieldsObj.fields().forEachRemaining(e -> fields.put(e.getKey(), e.getValue().asText()));
                out.add(new CredentialRecord(persona, provider, fields));
            }
            return out;
        } catch (Exception e) {
            throw new IOException("decrypt/parse failure: " + e.getMessage(), e);
        }
    }

    private void writeAll(List<CredentialRecord> items) throws IOException {
        Files.createDirectories(credsFile.getParent());

        // build plaintext JSON
        var root = M.createObjectNode();
        root.put("version", 1);
        var entries = root.putArray("entries");
        for (var r : items) {
            ObjectNode n = entries.addObject();
            n.put("persona", r.persona());
            n.put("provider", r.provider());
            var f = n.putObject("fields");
            r.fields().forEach(f::put);
        }
        var plain = M.writeValueAsBytes(root);

        // derive, encrypt, envelope
        try {
            byte[] salt = Crypto.random(16);
            byte[] nonce = Crypto.random(12);
            byte[] key = Crypto.deriveKey(passphrase, salt);
            byte[] ct = Crypto.encryptAesGcm(key, nonce, plain);

            var env = M.createObjectNode();
            env.put("v", 1);
            env.put("salt", Crypto.b64(salt));
            env.put("nonce", Crypto.b64(nonce));
            env.put("ct", Crypto.b64(ct));

            // atomic write
            Path tmp = credsFile.resolveSibling(credsFile.getFileName() + ".tmp");
            Files.writeString(tmp, M.writeValueAsString(env), StandardCharsets.UTF_8, CREATE, TRUNCATE_EXISTING, WRITE);
            Files.move(tmp, credsFile, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
        } catch (Exception e) {
            throw new IOException("encrypt/write failure: " + e.getMessage(), e);
        }
    }
}
