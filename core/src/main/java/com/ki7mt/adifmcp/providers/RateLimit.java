package com.ki7mt.adifmcp.providers;

import java.time.Instant;
import java.util.Optional;

/**
 * Represents rate limit information for a provider client.
 *
 * The {@code RateLimit} record encapsulates details about the current state
 * of rate limiting imposed by a provider. It includes:
 * - The number of remaining requests that can be made within the current limit.
 * - The time at which the rate limit resets.
 * - The maximum number of requests allowed within a specific time window.
 *
 * This record is typically used in conjunction with the {@code rateLimitInfo}
 * method in the {@code ProviderClient} interface to monitor and manage request rates
 * when interacting with provider services.
 *
 * The fields are optional to account for cases where some pieces of rate limit
 * information may not be provided by the provider.
 *
 * @param remaining The number of requests remaining in the current rate limit window.
 * @param resetAt   The timestamp at which the rate limit window resets.
 * @param limit     The total number of requests allowed in the rate limit window.
 */
public record RateLimit(Optional<Integer> remaining, Optional<Instant> resetAt, Optional<Integer> limit) {

}
