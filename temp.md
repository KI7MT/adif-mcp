core/
    build.gradle.kts
    src/main/java/com/ki7mt/adifmcp/adif/Qso.java
    src/main/java/com/ki7mt/adifmcp/credentials/CredentialStore.java
    src/main/java/com/ki7mt/adifmcp/providers/ProviderClient.java
    src/main/java/com/ki7mt/adifmcp/sync/SyncState.java
mkdir -f ./core/src/main/java/com/ki7mt/adifmcp/{sync,providers,credentials,adif}

cli/
    build.gradle.kts
    src/main/java/com/ki7mt/adifmcp/Main.java   # your Picocli root
    src/main/java/com/ki7mt/adifmcp/cli/creds/CredsCommand.java
    src/main/java/com/ki7mt/adifmcp/cli/sync/SyncCommand.java
mkdir -p ./cli/src/main/java/com/ki7mt/adifmcp/cli/{creds,sync}

ui/
    build.gradle.kts
    src/main/java/com/ki7mt/adifmcp/ui/HelloApp.java
mkdir -p ./ui/src/main/java/com/ki7mt/adifmcp/ui


server/
    build.gradle.kts
    src/main/java/com/ki7mt/adifmcp/server/ServerMain.java   # stub for now
mkdir -p  ./server/src/main/java/com/ki7mt/adifmcp/server

providers/provider-qrz/
    build.gradle.kts
    providers/provider-qrz/src/main/java/com/ki7mt/adifmcp/providers/qrz
    providers/provider-qrz/src/main/resources/META-INF/services

mkdir -p providers/provider-qrz/src/main/java/com/ki7mt/adifmcp/providers/qrz
mkdir -p providers/provider-qrz/src/main/resources/META-INF/services


providers/provider-clublog/
    build.gradle.kts
    providers/provider-clublog/src/main/java/com/ki7mt/adifmcp/providers/clublog
    providers/provider-clublog/src/main/resources/META-INF/services

mkdir -p providers/provider-clublog/src/main/java/com/ki7mt/adifmcp/providers/clublog
mkdir -p providers/provider-clublog/src/main/resources/META-INF/services

providers/provider-eqsl/
    build.gradle.kts
    providers/provider-eqsl/src/main/java/com/ki7mt/adifmcp/providers/eqsl
    providers/provider-eqsl/src/main/resources/META-INF/services

mkdir -p providers/provider-eqsl/src/main/java/com/ki7mt/adifmcp/providers/eqsl
mkdir -p providers/provider-eqsl/src/main/resources/META-INF/services

providers/provider-lotw/
    build.gradle.kts
    providers/provider-lotw/src/main/java/com/ki7mt/adifmcp/providers/lotw
    providers/provider-lotw/src/main/resources/META-INF/services

mkdir -p providers/provider-lotw/src/main/java/com/ki7mt/adifmcp/providers/lotw
mkdir -p providers/provider-lotw/src/main/resources/META-INF/services
