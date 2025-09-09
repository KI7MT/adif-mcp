package com.ki7mt.adifmcp.adif;

import java.time.Instant;
import java.util.Map;

public record Qso(String call, Instant qsoDateTime, Map<String,String> extras) {}
