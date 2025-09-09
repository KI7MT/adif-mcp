package com.ki7mt.adifmcp.providers;

public sealed interface ProviderCredentials permits UserPassCredentials, ApiKeyCredentials {
}
