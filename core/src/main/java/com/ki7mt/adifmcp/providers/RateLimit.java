package com.ki7mt.adifmcp.providers;

import java.time.Instant;
import java.util.Optional;

public record RateLimit(Optional<Integer> remaining, Optional<Instant> resetAt, Optional<Integer> limit) {

}
