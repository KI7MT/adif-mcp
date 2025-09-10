package io.adifmcp.spi;

import java.time.Instant;

/**
 * Providers MUST return raw ADIF text; higher layers parse/persist.
 */
public record FetchResult(String adif, Instant from, Instant to) {

}
