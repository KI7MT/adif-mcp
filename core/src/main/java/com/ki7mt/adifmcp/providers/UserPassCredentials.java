package com.ki7mt.adifmcp.providers;

public record UserPassCredentials(String username, String password) implements ProviderCredentials {

}
