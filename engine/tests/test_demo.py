"""Step 10: offline run, golden card output, and the demo fixture pairs."""
import json
import os
import socket
from datetime import date
from pathlib import Path

import pytest

from rotate_engine import build_cards, default_request
from rotate_engine import io as engine_io
from rotate_engine.io import root
from rotate_engine.models import CardSet

SPEC = json.loads((root() / "fixtures" / "requests" / "demo_requests.json").read_text())
DECISION = date.fromisoformat(SPEC["decision_date"])
GOLDEN = Path(__file__).parent / "golden" / "cards_ctg.json"


def demo(name: str) -> CardSet:
    item = SPEC["fixtures"][name]
    return build_cards(default_request(item["site"], DECISION, **item["request"]))


def normalise(obj):
    """Rounded floats, no timestamp: what the golden comparison looks at."""
    if isinstance(obj, dict):
        return {k: normalise(v) for k, v in obj.items() if k != "generated_at"}
    if isinstance(obj, list):
        return [normalise(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 3)
    return obj


def test_engine_runs_offline(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("the engine tried to open a network socket")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    engine_io._parse_json.cache_clear()  # force real file reads under the patch
    for name in SPEC["fixtures"]:
        assert isinstance(demo(name), CardSet), name


def test_cards_golden():
    current = normalise(json.loads(demo("cards_ctg").model_dump_json()))
    if os.environ.get("UPDATE_GOLDEN") == "1":
        GOLDEN.write_text(json.dumps(current, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    assert GOLDEN.exists(), "no golden file: run once with UPDATE_GOLDEN=1"
    assert current == json.loads(GOLDEN.read_text()), \
        "card output changed; if intended, rerun with UPDATE_GOLDEN=1 and review the diff"


@pytest.mark.parametrize("name", list(SPEC["fixtures"]))
def test_fixture_files_match_engine(name):
    """fixtures/*.json are current: regenerate with scripts/build_fixtures.py."""
    on_disk = normalise(json.loads((root() / "fixtures" / f"{name}.json").read_text()))
    assert on_disk == normalise(json.loads(demo(name).model_dump_json())), \
        f"fixtures/{name}.json is stale: run python scripts/build_fixtures.py"


def test_two_farms_same_weather_give_different_cards():
    a, b = demo("cards_ctg_farm_a"), demo("cards_ctg")
    assert a.analogs == b.analogs and a.window == b.window  # same weather evidence
    names = lambda cs: [c.strategy.name for c in cs.cards[1:]]
    assert not set(names(a)) & set(names(b))  # cards 2 and 3 fully different


def test_two_regions_two_hazards():
    ctg, barind = demo("cards_ctg"), demo("cards_barind")
    assert (ctg.site.hazard, barind.site.hazard) == ("salinity", "drought")
    assert ctg.analogs.weather_pool != barind.analogs.weather_pool


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_ndvi_fixture_files_match_engine(site_id):
    from rotate_engine import ndvi_series
    on_disk = json.loads((root() / "fixtures" / f"ndvi_{site_id}.json").read_text())
    assert normalise(on_disk) == normalise(json.loads(ndvi_series(site_id).model_dump_json())), \
        f"fixtures/ndvi_{site_id}.json is stale: run python scripts/build_fixtures.py"


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_ndvi_extras_fixture_files_match_engine(site_id):
    from rotate_engine import ndvi_series
    on_disk = json.loads((root() / "fixtures" / f"ndvi_{site_id}_extras.json").read_text())
    fresh = ndvi_series(site_id, date(2023, 11, 1), aqua=True, window=True)
    assert normalise(on_disk) == normalise(json.loads(fresh.model_dump_json())), \
        f"fixtures/ndvi_{site_id}_extras.json is stale: run python scripts/build_fixtures.py"


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_ndvi_hls_fixture_files_match_engine(site_id):
    from rotate_engine import ndvi_series
    on_disk = json.loads((root() / "fixtures" / f"ndvi_{site_id}_hls.json").read_text())
    assert normalise(on_disk) == normalise(json.loads(ndvi_series(site_id, hls=True).model_dump_json())), \
        f"fixtures/ndvi_{site_id}_hls.json is stale: run python scripts/build_fixtures.py"


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_ndvi_years_fixture_files_match_engine(site_id):
    from rotate_engine import ndvi_for_years
    on_disk = json.loads((root() / "fixtures" / f"ndvi_years_{site_id}.json").read_text())
    fresh = ndvi_for_years(site_id, [y["year"] for y in on_disk["years"]])
    assert normalise(on_disk) == normalise(json.loads(fresh.model_dump_json())), \
        f"fixtures/ndvi_years_{site_id}.json is stale: run python scripts/build_fixtures.py"


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_backtest_fixture_files_match_engine(site_id):
    from rotate_engine import run_backtest
    on_disk = json.loads((root() / "fixtures" / f"backtest_{site_id}.json").read_text())
    fresh = run_backtest(site_id, date.fromisoformat(on_disk["decision_date"]))
    assert normalise(on_disk) == normalise(json.loads(fresh.model_dump_json())), \
        f"fixtures/backtest_{site_id}.json is stale: run python scripts/build_fixtures.py"
