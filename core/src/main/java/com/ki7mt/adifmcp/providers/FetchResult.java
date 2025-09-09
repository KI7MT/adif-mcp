package com.ki7mt.adifmcp.providers;

import java.util.List;
import java.util.Optional;

public record FetchResult(List<com.ki7mt.adifmcp.adif.Qso> items, Optional<String> nextPageCursor) {

    public static FetchResult empty() {
        return new FetchResult(List.of(), Optional.empty());
    }
}
