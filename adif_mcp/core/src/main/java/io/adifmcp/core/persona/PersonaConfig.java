package io.adifmcp.core.persona;

import java.util.List;

/**
 * Root YAML model for persona configuration.
 */
public record PersonaConfig(
        /**
         * Schema version of the file.
         */
        int version,
        /**
         * All configured personas.
         */
        List<Persona> personas
        ) {

    /**
     * Ensures version is positive and lists are non-null/immutable.
     */
    public PersonaConfig  {
        personas = (personas == null) ? List.of() : List.copyOf(personas);
        if (version <= 0) {
            throw new IllegalArgumentException("version must be > 0");
        }
    }
}
