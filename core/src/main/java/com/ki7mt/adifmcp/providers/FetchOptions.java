package com.ki7mt.adifmcp.providers;

public record FetchOptions(int pageSize) {

    public static final FetchOptions DEFAULT = new FetchOptions(500);
}
