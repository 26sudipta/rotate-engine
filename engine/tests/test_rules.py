import json

import pytest

from rotate_engine.io import root
from rotate_engine.rules import RuleTable, load_rules, salinity_fit, water_rel_boro


def raw_rules() -> dict:
    return json.loads((root() / "rules" / "rules.json").read_text())


def test_rules_file_validates():
    table = load_rules()
    assert table.crops and table.patterns


def test_every_benefit_has_a_known_citation():
    table = load_rules()
    ids = {c.citation_id for c in table.citations}
    for crop in table.crops:
        assert all(b.citation_id in ids for b in crop.benefits), crop.crop_id


def test_value_without_citation_is_rejected():
    data = raw_rules()
    t_aman = next(c for c in data["crops"] if c["crop_id"] == "t_aman")
    t_aman["n_fix_kg_ha"] = [10, 20]
    with pytest.raises(ValueError, match="no citation covers it"):
        RuleTable.model_validate(data)


def test_unknown_citation_is_rejected():
    data = raw_rules()
    data["crops"][0]["risks"][0]["citation_id"] = "made_up_2026"
    with pytest.raises(ValueError, match="unknown citation"):
        RuleTable.model_validate(data)


def test_salinity_filter_reads_whole_season_only():
    table = load_rules()
    st = table.crop("boro_salt_tolerant")
    seedling_only = st.model_copy(update={"salinity_whole_season_max_dS_m": None})
    assert salinity_fit(seedling_only, "moderate_8_12", table) == "unsourced"
    low_whole_high_seedling = st.model_copy(update={"salinity_whole_season_max_dS_m": 3.0,
                                                    "salinity_seedling_dS_m": 20.0})
    assert salinity_fit(low_whole_high_seedling, "slight_4_8", table) == "exceeds"


def test_salinity_filter_examples():
    table = load_rules()
    assert salinity_fit(table.crop("boro"), "slight_4_8", table) == "exceeds"
    assert salinity_fit(table.crop("wheat"), "slight_4_8", table) == "ok"
    assert salinity_fit(table.crop("mungbean"), "slight_4_8", table) == "unsourced"
    assert salinity_fit(table.crop("boro"), "unknown", table) == "ok"


def test_water_relative_to_boro_needs_same_source():
    table = load_rules()
    assert water_rel_boro(table.crop("wheat"), table) == pytest.approx(304 / 2981, abs=1e-3)
    assert water_rel_boro(table.crop("mungbean"), table) is None
    assert water_rel_boro(table.crop("fallow"), table) == 0.0


def test_pattern_slots_and_seasons_align():
    data = raw_rules()
    data["patterns"][0]["seasons"] = ["rabi", "kharif1"]
    with pytest.raises(ValueError, match="slots but"):
        RuleTable.model_validate(data)


def test_rules_edit_is_picked_up_without_restart(tmp_path, monkeypatch):
    import os
    (tmp_path / "rules").mkdir()
    target = tmp_path / "rules" / "rules.json"
    target.write_text(json.dumps(raw_rules()))
    monkeypatch.setenv("ROTATE_ROOT", str(tmp_path))
    assert not load_rules().reviewed
    edited = raw_rules() | {"review_status": "reviewed"}
    target.write_text(json.dumps(edited))
    st = target.stat()
    os.utime(target, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))  # a later edit
    assert load_rules().reviewed
