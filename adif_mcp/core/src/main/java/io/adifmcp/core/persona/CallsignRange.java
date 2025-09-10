package io.adifmcp.core.persona;

import java.time.LocalDate;

/**
 * A callsign active over an optional date range. Null dates mean open-ended.
 */
public record CallsignRange(
        /**
         * Callsign text, e.g. "KI7MT".
         */
        String call,
        /**
         * Start date (inclusive) or null.
         */
        LocalDate from,
        /**
         * End date (inclusive) or null.
         */
        LocalDate to
        ) {

}
