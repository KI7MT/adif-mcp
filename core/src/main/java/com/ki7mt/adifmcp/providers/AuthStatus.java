package com.ki7mt.adifmcp.providers;

/**
 * Represents the authentication status for a provider client.
 *
 * The {@code AuthStatus} enum defines possible states of an authentication
 * check, which can indicate whether authentication was successful, failed,
 * expired, missing, or encountered an error.
 *
 * The possible values are: - {@code OK}: Authentication was successful. -
 * {@code INVALID}: The provided credentials are invalid. - {@code EXPIRED}: The
 * authentication has expired. - {@code MISSING}: Credentials are missing or not
 * provided. - {@code ERROR}: An error occurred during the authentication
 * process.
 *
 * This enum is typically used in conjunction with the {@code authCheck} method
 * in the {@code ProviderClient} interface to indicate the result of an
 * authentication attempt.
 */
public enum AuthStatus {
    OK, INVALID, EXPIRED, MISSING, ERROR
}
