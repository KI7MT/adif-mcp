package com.ki7mt.adifmcp.adif;

import java.time.Instant;
import java.util.Map;

/**
 * Represents a QSO (contact) record used in amateur radio logging systems.
 * This immutable record encapsulates the essential details of a QSO,
 * including the contact's call sign, the date and time of the QSO,
 * and any additional metadata or properties stored as key-value pairs.
 *
 * @param call         The call sign of the contacted station.
 * @param qsoDateTime  The date and time of the QSO, represented as an {@link Instant}.
 * @param extras       A map containing additional metadata or properties, stored as key-value pairs.
 */
public record Qso(String call, Instant qsoDateTime, Map<String,String> extras) {}
