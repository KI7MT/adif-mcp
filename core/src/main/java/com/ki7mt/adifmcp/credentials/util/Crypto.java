package com.ki7mt.adifmcp.credentials.util;

import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.util.Base64;

public final class Crypto {

    private static final SecureRandom RNG = new SecureRandom();
    private static final int SALT_LEN = 16;     // 128-bit salt
    private static final int NONCE_LEN = 12;    // 96-bit GCM nonce
    private static final int KEY_LEN = 256;     // 256-bit AES key
    private static final int PBKDF2_ITERS = 100_000;

    private Crypto() {
    }

    public static byte[] random(int n) {
        byte[] b = new byte[n];
        RNG.nextBytes(b);
        return b;
    }

    public static byte[] deriveKey(char[] passphrase, byte[] salt) throws Exception {
        var spec = new PBEKeySpec(passphrase, salt, PBKDF2_ITERS, KEY_LEN);
        var skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        return skf.generateSecret(spec).getEncoded();
    }

    public static byte[] encryptAesGcm(byte[] key, byte[] nonce, byte[] plain) throws Exception {
        var cipher = Cipher.getInstance("AES/GCM/NoPadding");
        var spec = new GCMParameterSpec(128, nonce);
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), spec);
        return cipher.doFinal(plain);
    }

    public static byte[] decryptAesGcm(byte[] key, byte[] nonce, byte[] ct) throws Exception {
        var cipher = Cipher.getInstance("AES/GCM/NoPadding");
        var spec = new GCMParameterSpec(128, nonce);
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key, "AES"), spec);
        return cipher.doFinal(ct);
    }

    public static String b64(byte[] data) {
        return Base64.getEncoder().encodeToString(data);
    }

    public static byte[] unb64(String s) {
        return Base64.getDecoder().decode(s);
    }
}
