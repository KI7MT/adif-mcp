#!/usr/bin/env python3
"""Generate enumerations_country.json from DXCC Entity Code enumeration.

The ADIF spec defines Country as the DXCC entity name. This script extracts
all Entity Names from enumerations_dxcc_entity_code.json and creates a
Country enumeration file. Deleted DXCC entities are marked Import-only.

One-time generator — output is committed as a static resource.
"""

import json
import os


def main() -> None:
    """Generate Country enumeration JSON from DXCC entities."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    spec_dir = os.path.join(
        script_dir, "..", "src", "adif_mcp", "resources", "spec", "316"
    )

    dxcc_path = os.path.join(spec_dir, "enumerations_dxcc_entity_code.json")
    with open(dxcc_path, "r", encoding="utf-8") as f:
        dxcc_data = json.load(f)

    dxcc_records = dxcc_data["Adif"]["Enumerations"]["DXCC_Entity_Code"]["Records"]

    country_records: dict[str, dict[str, str]] = {}
    for _key, rec in dxcc_records.items():
        entity_name = rec.get("Entity Name", "")
        entity_code = rec.get("Entity Code", "")

        # Skip entity code 0 ("None")
        if entity_code == "0":
            continue

        country_rec: dict[str, str] = {
            "Enumeration Name": "Country",
            "Country Name": entity_name,
            "DXCC Entity Code": entity_code,
        }

        # Deleted DXCC entities → Import-only (warn, not error)
        if rec.get("Deleted") == "true":
            country_rec["Import-only"] = "true"

        country_records[entity_name] = country_rec

    output = {
        "Adif": {
            "Enumerations": {
                "Country": {
                    "Header": [
                        "Enumeration Name",
                        "Country Name",
                        "DXCC Entity Code",
                        "Import-only",
                    ],
                    "Records": country_records,
                }
            }
        }
    }

    out_path = os.path.join(spec_dir, "enumerations_country.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total = len(country_records)
    deleted = sum(
        1 for r in country_records.values() if r.get("Import-only") == "true"
    )
    print(f"Generated {out_path}")
    active = total - deleted
    print(f"  Total: {total} countries ({active} active, {deleted} import-only)")


if __name__ == "__main__":
    main()
