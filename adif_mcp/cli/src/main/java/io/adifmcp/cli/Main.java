package io.adifmcp.cli;

import picocli.CommandLine;
import picocli.CommandLine.Command;

@Command(
        name = "adif-mcp",
        description = "ADIF MCP CLI",
        mixinStandardHelpOptions = true,
        versionProvider = Main.ManifestVersion.class
)
public class Main implements Runnable {

    @Override
    public void run() {
        // no-op; subcommands later
    }

    public static void main(String[] args) {
        int code = new CommandLine(new Main()).execute(args);
        System.exit(code);
    }

    /**
     * Prints "adif-mcp <version>" with robust fallback.
     */
    public static class ManifestVersion implements CommandLine.IVersionProvider {

        @Override
        public String[] getVersion() {
            // 1) Prefer Implementation-Version from JAR manifest
            String fromManifest = Main.class.getPackage().getImplementationVersion();
            if (fromManifest != null) {
                return new String[]{"adif-mcp " + fromManifest};
            }
            // 2) Fallback to build-info.properties (IDE/Gradle run)
            try (var in = Main.class.getResourceAsStream("/build-info.properties")) {
                if (in != null) {
                    var props = new java.util.Properties();
                    props.load(in);
                    String v = props.getProperty("version");
                    if (v != null && !v.isBlank()) {
                        return new String[]{"adif-mcp " + v};
                    }
                }
            } catch (Exception ignored) {
            }
            // 3) Last resort
            return new String[]{"adif-mcp dev"};
        }
    }
}
