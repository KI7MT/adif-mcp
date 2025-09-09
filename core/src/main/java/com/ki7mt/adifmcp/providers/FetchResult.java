package com.ki7mt.adifmcp.providers;

import java.util.List;
import java.util.Optional;

/**
 * Represents the result of a fetch operation that retrieves a list of QSOs
 * (contacts) from a provider and manages optional pagination data.
 *
 * The {@code FetchResult} record encapsulates:
 * - A list of {@code Qso} objects representing the fetched data items.
 * - An optional pagination cursor, which may be provided to enable fetching the next page of results.
 *
 * This record is designed to work with paginated fetch operations, where the
 * presence of a cursor in the result indicates that additional pages of data can
 * be fetched. If the cursor is absent, it implies the fetched data is complete.
 *
 * The {@code empty} method provides a way to create an empty result, containing
 * no QSOs and no pagination cursor.
 */
public record FetchResult(List<com.ki7mt.adifmcp.adif.Qso> items, Optional<String> nextPageCursor) {

    public static FetchResult empty() {
        return new FetchResult(List.of(), Optional.empty());
    }
}
