package com.ki7mt.adifmcp.providers;

/**
 * Represents configurable options for fetching data from a provider.
 *
 * The {@code FetchOptions} record is used to specify parameters such as the size
 * of each page of results when performing data fetch operations. This allows for
 * customizable pagination where the number of items per request can be adjusted.
 *
 * @param pageSize The number of items to fetch per page or batch. This controls
 *                 the granularity of the data retrieval process.
 */
public record FetchOptions(int pageSize) {

    public static final FetchOptions DEFAULT = new FetchOptions(500);
}
