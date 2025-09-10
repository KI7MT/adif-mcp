package io.adifmcp.spi;

/**
 * Optional tuning flags for fetch; keep minimal now.
 */
public record FetchOptions(boolean includeDeleted) {

    public static final FetchOptions DEFAULT = new FetchOptions(false);
}
