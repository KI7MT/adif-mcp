package io.adifmcp.core.persona;

import java.util.List;
import java.util.Map;

/**
 * Immutable persona definition.
 */
public record Persona(
        String id,
        String label,
        List<CallsignRange> callsigns,
        Map<String, ProviderFlags> providers
        ) {

    public Persona    {
        callsigns = List.copyOf(callsigns);
        providers = Map.copyOf(providers);
    }
}
