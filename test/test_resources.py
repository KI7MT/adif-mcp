"""Test import, verions, firlds and manifest shaoes for all JSON in resources/**"""

from adif_mcp.resources import (
    get_adif_catalog,
    get_adif_meta,
    get_manifest_schema,
    list_providers,
    load_provider,
)


def test_adif_meta_has_version() -> None:
    """TODO: add docstrings for: test adif meta has version"""
    meta = get_adif_meta()
    assert "spec_version" in meta


def test_adif_catalog_fields_nonempty() -> None:
    """TODO: add docstrings for: test catalog fields"""
    cat = get_adif_catalog()
    assert isinstance(cat.get("fields"), list) and cat["fields"]


def test_list_and_load_provider() -> None:
    """TODO: add docstrings for: test list and load provilages"""
    provs = list_providers()
    assert {"eqsl", "lotw", "qrz", "clublog"}.issubset(set(provs))
    eqsl = load_provider("eqsl")
    assert "fields" in eqsl


def test_manifest_schema_shape() -> None:
    """TODO: add docstrings for: test manifest schema shape"""
    schema = get_manifest_schema()
    assert schema.get("$schema") or schema.get("$id") or "type" in schema
