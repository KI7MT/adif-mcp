package com.ki7mt.adifmcp.providers;

/**
 * Represents the health status of a provider client.
 *
 * The {@code Health} record encapsulates the status and details of a health check
 * performed on a provider client. It includes a boolean indicating whether the
 * client is functioning correctly and a detailed message providing additional context.
 *
 * This record is typically used in the context of the {@code ping} method in the
 * {@code ProviderClient} interface to determine if the provider is responsive and
 * operational.
 *
 * @param ok     Indicates whether the health check was successful (true) or not (false).
 * @param detail A message providing further details about the health status.
 */
public record Health(boolean ok, String detail) {

}
