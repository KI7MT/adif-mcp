package io.adifmcp.spi;

import java.time.Instant;

/**
 * Snapshot of provider rate limit state (if known).
 */
public record RateLimit(Integer remaining, Instant resetAt) {

}
