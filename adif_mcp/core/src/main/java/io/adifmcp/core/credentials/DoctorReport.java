package io.adifmcp.core.credentials;

import java.util.Map;

/**
 * Non-secret health summary for the credential store backend.
 */
public record DoctorReport(
        boolean ok,
        String backend,
        Map<String, Object> details
        ) {

}
