"""Regression tests for bugs found in the full code review (5 Nov 2026)."""
import importlib.util
import json
from datetime import date

import pandas as pd
import pytest

from rotate_engine import cards_for_site, find_analogs, pipeline
from rotate_engine.__main__ import main
from rotate_engine.io import root
from rotate_engine.models import CardSet, NotCached
from rotate_engine.provenance import ndvi_provenance
from rotate_engine.rules import load_rules, salinity_fit
from rotate_engine.seasons import InsufficientWindowError

DECISION = date(2026, 11, 13)


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, root() / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---- unknown rotation id ------------------------------------------------------------------------

def test_unknown_rotation_is_a_clear_value_error():
    with pytest.raises(ValueError, match="unknown current_rotation"):
        cards_for_site("ctg_anwara", DECISION, current_rotation="boro-wheat")


def test_cli_unknown_rotation_exit_2(tmp_path, capsys):
    req = tmp_path / "r.json"
    req.write_text('{"current_rotation": "boro-wheat"}')
    assert main(["cards", "--site", "ctg_anwara", "--date", "2026-11-13", "--input", str(req)]) == 2
    assert "unknown current_rotation" in capsys.readouterr().err


# ---- 2-4 dS/m class is filtered -----------------------------------------------------------------

def test_very_slight_class_filters_sensitive_crops():
    rules = load_rules()
    for crop in ("maize", "potato", "onion", "chilli", "sweet_potato"):
        assert salinity_fit(rules.crop(crop), "very_slight_2_4", rules) == "exceeds", crop
    assert salinity_fit(rules.crop("maize"), "non_saline_lt2", rules) == "ok"


def test_very_slight_class_warns_on_boro():
    cs = cards_for_site("ctg_anwara", DECISION, salinity_class="very_slight_2_4")
    assert any("reaches 4 dS/m" in r.text for r in cs.cards[0].risks)


def test_unknown_class_adds_no_salt_risks():
    cs = cards_for_site("ctg_anwara", DECISION, salinity_class="unknown")
    assert not any("salinity class" in r.text for c in cs.cards for r in c.risks)


# ---- no repeated rotation when the farm is already fallow at high salinity ----------------------

def test_fallow_farm_at_high_salinity_gets_three_different_cards():
    cs = cards_for_site("ctg_anwara", DECISION, current_rotation="fallow-fallow-t_aman",
                        salinity_class="moderate_8_12")
    assert len({tuple(c.strategy.slots) for c in cs.cards}) == 3
    assert "8 dS/m or more" in cs.cards[0].why


# ---- too little history -------------------------------------------------------------------------

@pytest.mark.parametrize("decision", [date(1999, 11, 13), date(2001, 11, 13), date(1981, 3, 1)])
def test_too_few_past_seasons_is_a_clear_error(decision):
    with pytest.raises(InsufficientWindowError):
        find_analogs("barind_godagari", decision)


def test_too_few_ndvi_years_means_ndvi_pending():
    res = find_analogs("barind_godagari", date(2004, 11, 13))  # NDVI years 2001-2004 only: 4 < 5
    assert res.ndvi_status == "pending" and res.confidence is None and res.analogs.ndvi_pool == []
    assert isinstance(cards_for_site("barind_godagari", date(2004, 11, 13)), NotCached)


def test_site_missing_from_ndvi_file_is_pending(monkeypatch):
    real = pipeline.get_site
    monkeypatch.setattr(pipeline, "get_site",
                        lambda sid: real(sid) | {"ndvi_id": "not_in_the_csv"})
    res = find_analogs("ctg_anwara", DECISION)
    assert res.ndvi_status == "pending" and res.confidence is None


# ---- scripts -------------------------------------------------------------------------------------

def test_fetch_power_refuses_bad_responses():
    fp = load_script("fetch_power")
    body = {"header": {"fill_value": -999.0}, "messages": [],
            "properties": {"parameter": {"RH2M": {"20260101": -999.0, "20260102": -999.0},
                                         "T2M_MIN": {"20260101": 20.0, "20260102": 21.0}}}}
    df = fp.to_table(body)
    assert df["RH2M"].isna().all()
    assert "no valid values" in fp.bad_response(body, df)
    assert "messages" in fp.bad_response(body | {"messages": ["not available in LST"]}, df)
    good = body | {"properties": {"parameter": {"T2M_MIN": {"20260101": 20.0}}}}
    assert fp.bad_response(good, fp.to_table(good)) is None


def test_ndvi_script_manifest_is_readable_by_engine(tmp_path, monkeypatch):
    nd = load_script("fetch_ndvi_appeears")
    assert b"user_id" not in nd.strip_user(b'{"task_id": "t", "user_id": "someone@example.org"}')
    (tmp_path / "data" / "ndvi").mkdir(parents=True)
    manifest = nd.build_manifest("t", [{"file_name": "x-MOD13Q1-061-results.csv", "sha256": "abc"}],
                                 date(2026, 11, 5))
    (tmp_path / "data" / "ndvi" / "bundle_manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setenv("ROTATE_ROOT", str(tmp_path))
    prov = ndvi_provenance()
    assert prov.route == "appeears" and prov.sha256 == "abc" and str(prov.accessed) == "2026-11-05"


def test_committed_ndvi_request_has_no_user_id():
    for path in (root() / "data" / "ndvi").glob("*-request.json"):
        assert "user_id" not in json.loads(path.read_text()), path.name


# ---- high salinity prefers a sourced salt-tolerant option ---------------------------------------

def test_high_salinity_card_2_is_sourced_tolerant_option():
    cs = cards_for_site("ctg_anwara", DECISION, salinity_class="moderate_8_12")
    assert "boro_salt_tolerant" in cs.cards[1].strategy.slots
    assert "sourced whole-season salt tolerance" in cs.cards[1].why
    assert cs.cards[2].strategy.name == "Fallow, short oilseed, or local review"


def test_above_all_sourced_values_falls_back_to_unsourced_option():
    cs = cards_for_site("ctg_anwara", DECISION, salinity_class="strong_12_16")
    assert "boro_salt_tolerant" not in cs.cards[1].strategy.slots  # 8 dS/m < 12
    assert any("salinity tolerance" in g for g in cs.cards[1].gaps)
