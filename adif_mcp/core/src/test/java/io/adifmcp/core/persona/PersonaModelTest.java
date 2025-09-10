package io.adifmcp.core.persona;

import static org.junit.jupiter.api.Assertions.*;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class PersonaModelTest {

    @Test
    @DisplayName("Persona records construct with copied collections")
    void personaConstructs() {
        var calls = List.of(new CallsignRange("KI7MT", LocalDate.of(2020, 1, 1), null));
        var provs = Map.of("eqsl", new ProviderFlags(true));

        var p = new Persona("KI7MT", "Primary", calls, provs);

        assertEquals("KI7MT", p.id());
        assertEquals("Primary", p.label());
        assertEquals(1, p.callsigns().size());
        assertTrue(p.providers().get("eqsl").enabled());
    }
}
