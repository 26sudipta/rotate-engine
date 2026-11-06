"""Regenerate fixtures/*.json from the engine: card sets from fixtures/requests/demo_requests.json,
one NDVI curve per site (ndvi_<site>.json), the same from Nov 2023 with Aqua points and the
3x3-pixel spread (ndvi_<site>_extras.json), the 30 m HLS curve (ndvi_<site>_hls.json), the Boro-season curves of each site's NDVI
look-alike years for the demo date (ndvi_years_<site>.json), and each site's backtest
(backtest_<site>.json).

Usage: python scripts/build_fixtures.py
Offline: reads only data/ and rules/ through rotate_engine. Rerun after any data, rules or code change.
"""
import json
import sys
from datetime import date
from pathlib import Path

from rotate_engine import (build_cards, default_request, find_analogs, list_sites, ndvi_for_years,
                           ndvi_series, run_backtest)
from rotate_engine.models import AnalogResult, BacktestResult, CardSet, NdviSeries, NdviYears

ROOT = Path(__file__).resolve().parents[1]
EXTRAS_FROM = date(2023, 11, 1)  # the 3x3 window starts here (scripts/fetch_ndvi_ornl.py)


def main() -> int:
    spec = json.loads((ROOT / "fixtures" / "requests" / "demo_requests.json").read_text())
    decision = date.fromisoformat(spec["decision_date"])
    failed = False
    for name, item in spec["fixtures"].items():
        result = build_cards(default_request(item["site"], decision, **item["request"]))
        if not isinstance(result, CardSet):
            print(f"FAILED {name}: {result.message}", file=sys.stderr)
            failed = True
            continue
        (ROOT / "fixtures" / f"{name}.json").write_text(result.model_dump_json(indent=2) + "\n")
        print(f"fixtures/{name}.json: " + " | ".join(c.strategy.name for c in result.cards))
    for site in list_sites():  # full greenness curve per site, for the NDVI chart
        series = ndvi_series(site.id)
        if not isinstance(series, NdviSeries) or series.status != "ok":
            print(f"FAILED ndvi_{site.id}: NDVI pending", file=sys.stderr)
            failed = True
            continue
        (ROOT / "fixtures" / f"ndvi_{site.id}.json").write_text(series.model_dump_json(indent=2) + "\n")
        print(f"fixtures/ndvi_{site.id}.json: {len(series.points)} points, {len(series.gaps)} cloud gaps")
        extras = ndvi_series(site.id, EXTRAS_FROM, aqua=True, window=True)
        if not isinstance(extras, NdviSeries) or extras.status != "ok":
            print(f"FAILED ndvi_{site.id}_extras: {getattr(extras, 'message', 'NDVI pending')}", file=sys.stderr)
            failed = True
        else:
            (ROOT / "fixtures" / f"ndvi_{site.id}_extras.json").write_text(extras.model_dump_json(indent=2) + "\n")
            print(f"fixtures/ndvi_{site.id}_extras.json: {len(extras.points)} points (Terra + Aqua), "
                  f"{len(extras.window_3x3)} 3x3 windows")
        hls = ndvi_series(site.id, hls=True)  # separate 30 m curve, display only
        if not isinstance(hls, NdviSeries) or hls.status != "ok":
            print(f"FAILED ndvi_{site.id}_hls: {getattr(hls, 'message', 'HLS pending')}", file=sys.stderr)
            failed = True
        else:
            (ROOT / "fixtures" / f"ndvi_{site.id}_hls.json").write_text(hls.model_dump_json(indent=2) + "\n")
            print(f"fixtures/ndvi_{site.id}_hls.json: {len(hls.points)} HLS 30 m points")
        analogs = find_analogs(site.id, decision)  # season curves of the NDVI look-alike years
        years = [a.year for a in analogs.analogs.ndvi_pool] if isinstance(analogs, AnalogResult) else []
        per_year = ndvi_for_years(site.id, years)
        if not years or not isinstance(per_year, NdviYears) or per_year.status != "ok":
            print(f"FAILED ndvi_years_{site.id}: no NDVI look-alike years", file=sys.stderr)
            failed = True
            continue
        (ROOT / "fixtures" / f"ndvi_years_{site.id}.json").write_text(per_year.model_dump_json(indent=2) + "\n")
        print(f"fixtures/ndvi_years_{site.id}.json: years {years}")
        bt = run_backtest(site.id, decision)
        if not isinstance(bt, BacktestResult):
            print(f"FAILED backtest_{site.id}: {bt.message}", file=sys.stderr)
            failed = True
            continue
        (ROOT / "fixtures" / f"backtest_{site.id}.json").write_text(bt.model_dump_json(indent=2) + "\n")
        print(f"fixtures/backtest_{site.id}.json: {bt.verdict_text}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
