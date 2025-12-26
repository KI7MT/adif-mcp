
# Award Query Workflow Examples

Amateur Radio operators don’t just make QSOs — they track and confirm them to
pursue awards, challenges, and special programs. These awards provide goals,
recognition, and a sense of achievement that keeps operating fun, motivating
and educational.

ADIF-MCP provides a foundation to query logbooks in ways that directly support
award tracking. Whether you’re chasing **DXCC**, **WAS**, or a niche program
like **SOTA** or **30m Digital Group**, the same core QSO data (callsign, band,
mode, date, confirmation) can be filtered and summarized to answer questions
like:

- *“Which DXCC entities have I confirmed on 20m CW?”*
- *“How many US States do I still need on FT8?”*
- *“Are my SOTA activations properly logged and confirmed?”*

This section introduces the major award sponsors and the types of queries that
matter for each. While each sponsor has its own rules and requirements, all of
them build on the same ADIF fields — making MCP an ideal bridge between your
logbook and the awards you care about.

>IMPORTANT - ADIF-MCP does not try to “own” awards. Instead, it provides a **safe, typed backbone** to query QSO data in ways that award sponsors already define. MCP aligns to the [ADIF 3.1.6 spec](https://adif.org.uk/316/ADIF_316.htm), including the official [`SponsoredAward` enumeration](https://adif.org.uk/316/ADIF_316.htm#SponsoredAward_Enumeration).


---

## Core Sponsors in ADIF

This matrix captures **who sponsors what** and how MCP can expose it to operators through Integrations. As we all kknow, this is just a "small" sampling of whats available.

| Sponsor | Focus | Notes |
|---------|-------|-------|
| **ARRL** | LoTW, DXCC, WAS, VUCC, Triple Play, Challenge | Premier award sponsor; strict QSO matching, digital signing via LoTW |
| **CQ Magazine** | WPX, WAZ, WW Contest Awards | Contest-centric; CQ World Wide DX Contest is globally recognized |
| **DARC (Germany)** | DLD (German Districts), WAE (Worked All Europe) | Strong EU/region-based award programs |
| **eQSL** | eDX100, eWAS, eCanada, etc. | Looser confirmation rules; parallel awards to ARRL/CQ |
| **RSGB (UK)** | Islands on the Air (IOTA) | Geographic/island award system, now standalone but ADIF-aligned |
| **Other Programs** | SOTA, POTA, County Hunters, 30MDG, etc. | May not appear in ADIF’s enumeration, but use ADIF fields |

---

## How MCP Tracks Coverage

1. **Spec Layer**
   - ADIF defines the field names (`call`, `dxcc`, `state`, `cqz`, `iota_ref`, etc.) and sponsor enumerations.
   - MCP maps these to canonical `QsoRecord` fields.

2. **Provider Layer**
   - LoTW, eQSL, QRZ, Club Log expose *subsets* of ADIF fields.
   - MCP normalizes them to a common schema.

3. **Persona Layer**
   - Operators (DXers, Contesters, SOTA/POTA activators, casual loggers) query their logs in plain language.
   - MCP ensures those queries resolve only against valid fields/sponsors.

---

## Persona → Award → Field Mapping (Examples)

| Persona | Typical Award Goal | Key ADIF Fields | Example Query |
|---------|-------------------|-----------------|---------------|
| **DXer** | DXCC (ARRL), WAZ (CQ) | `dxcc`, `cqz`, `band`, `mode` | “How many DXCC entities confirmed on 20m FT8?” |
| **Contester** | CQ WPX, CQ WW | `call`, `prefix`, `contest_id` | “Show my confirmed prefixes from last WPX contest” |
| **State Chaser** | WAS (ARRL/eQSL) | `state`, `band`, `mode` | “Which states do I still need on CW?” |
| **SOTA Activator/Hunter** | SOTA (community) | `my_sota_ref`, `sota_ref` | “List my 2024 SOTA activations by summit code” |
| **POTA Enthusiast** | POTA (community) | `my_sig`, `sig_info` | “Which parks have I activated this year?” |
| **County Hunter** | MARAC / USA-CA | `cnty` | “Which counties do I still need on 40m?” |

---

## Coverage Percentage (Concept)

- **Denominator** = All ADIF fields relevant to awards (from catalog).
- **Numerator** = Fields MCP supports via QsoRecord + Provider Integrations.
- **Output** = Coverage % (per provider, per sponsor, per persona).

This gives a simple way to say:
- “MCP covers 85% of ARRL award fields”
- “MCP covers 60% of CQ contest awards”
- “MCP covers 95% of SOTA/POTA fields used in the wild”

---

## Notes

This list is not exhaustive — new awards, challenges, and operating programs
emerge all the time. ADIF-MCP’s role is **not** to enforce award rules or
certify results, but to provide the reliable data plumbing needed for
award-tracking tools, logbook providers, and operators to build upon.

By keeping the MCP layer focused on **safe, typed access to QSO data**, it
remains flexible enough to support both long-standing awards like **DXCC** and
emerging community programs yet to be defined.

---

🔑 **Takeaway**: MCP doesn’t replace LoTW, eQSL, or award programs. Instead, it gives operators *visibility and accessibility* into their award progress, across sponsors, without them needing to export, filter, or code.
