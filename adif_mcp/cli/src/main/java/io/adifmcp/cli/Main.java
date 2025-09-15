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
        new CommandLine(this).usage(System.out);
    }

    public static void main(String[] args) {
        CommandLine root = new CommandLine(new Main());
        root.addSubcommand("providers", new Providers());
        root.addSubcommand("serve", new Serve());
        System.exit(root.execute(args));
    }

    static class ManifestVersion implements CommandLine.IVersionProvider {

        @Override
        public String[] getVersion() throws Exception {
            // 1) JAR manifest (works when running packaged)
            String manifestVersion = Main.class.getPackage().getImplementationVersion();

            // 2) Fallback: build-info.properties (works with :cli:run)
            String resourceVersion = null;
            try (var in = Main.class.getResourceAsStream("/build-info.properties")) {
                if (in != null) {
                    var props = new java.util.Properties();
                    props.load(in);
                    resourceVersion = props.getProperty("version");
                }
            }

            String v = manifestVersion != null ? manifestVersion
                    : (resourceVersion != null ? resourceVersion : "dev");
            return new String[]{"adif-mcp " + v};
        }
    }
}
