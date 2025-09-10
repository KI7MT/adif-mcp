package io.adifmcp.spi;

import java.nio.file.Path;

/**
 * Non-secret runtime context passed to providers.
 */
public record ProviderContext(Path ssotRoot) {

}
