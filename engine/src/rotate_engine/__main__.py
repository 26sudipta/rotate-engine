"""CLI: python -m rotate_engine {sites,features,analogs,cards,backtest,ndvi,ndvi-years,schemas} ..."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from .io import NotCachedError
from .models import json_schemas
from .pipeline import (cards_for_site, find_analogs, list_sites, ndvi_for_years, ndvi_series, run_backtest,
                       season_features)
from .seasons import InsufficientWindowError


def _write(text: str, out: str | None) -> None:
    if out:
        Path(out).write_text(text + "\n")
    else:
        print(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rotate_engine", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sites", help="list cached sites as JSON")
    for name, help_text in (("features", "print the per-season feature table"),
                            ("analogs", "analog years for a site and decision date (JSON)"),
                            ("cards", "three strategy cards (JSON)"),
                            ("backtest", "leave-one-year-out skill of the NDVI analogs (JSON)")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--site", required=True)
        p.add_argument("--date", type=date.fromisoformat, default=date.today(),
                       help="decision date YYYY-MM-DD (default: today)")
        p.add_argument("--out")
        if name == "cards":
            p.add_argument("--input", help="JSON with request fields: current_rotation, "
                           "salinity_class, priorities, constraints")
    p = sub.add_parser("ndvi", help="greenness curve for a site (JSON)")
    p.add_argument("--site", required=True)
    p.add_argument("--from", dest="start", type=date.fromisoformat, help="first day YYYY-MM-DD")
    p.add_argument("--to", dest="end", type=date.fromisoformat, help="last day YYYY-MM-DD")
    p.add_argument("--aqua", action="store_true", help="interleave Aqua (MYD13Q1) points")
    p.add_argument("--window", action="store_true", help="add the 3x3-pixel spread (Nov 2023 on)")
    p.add_argument("--hls", action="store_true", help="the separate 30 m HLS curve (not with --aqua/--window)")
    p.add_argument("--out")
    p = sub.add_parser("ndvi-years", help="one Boro-season greenness curve per harvest year (JSON)")
    p.add_argument("--site", required=True)
    p.add_argument("--years", required=True, type=int, nargs="+", help="Boro harvest years, e.g. 2014 2019")
    p.add_argument("--aqua", action="store_true", help="interleave Aqua (MYD13Q1) points")
    p.add_argument("--out")
    p = sub.add_parser("schemas", help="export JSON schemas")
    p.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    try:
        if args.cmd == "sites":
            _write(json.dumps([s.model_dump() for s in list_sites()], indent=2), None)
        elif args.cmd == "features":
            window, table, skipped, warnings = season_features(args.site, args.date)
            with pd.option_context("display.max_rows", None, "display.width", 140):
                print(table.round(2).to_string())
            print(f"\ncurrent season {window.season_year}: window {window.start}..{window.end}")
            print(f"skipped seasons: {skipped or 'none'}")
            for w in warnings:
                print(f"warning: {w}")
        elif args.cmd == "analogs":
            _write(find_analogs(args.site, args.date).model_dump_json(indent=2), args.out)
        elif args.cmd == "cards":
            overrides = json.loads(Path(args.input).read_text()) if args.input else {}
            _write(cards_for_site(args.site, args.date, **overrides).model_dump_json(indent=2), args.out)
        elif args.cmd == "ndvi":
            _write(ndvi_series(args.site, args.start, args.end, args.aqua, args.window, args.hls)
                   .model_dump_json(indent=2), args.out)
        elif args.cmd == "backtest":
            _write(run_backtest(args.site, args.date).model_dump_json(indent=2), args.out)
        elif args.cmd == "ndvi-years":
            _write(ndvi_for_years(args.site, args.years, args.aqua).model_dump_json(indent=2), args.out)
        elif args.cmd == "schemas":
            out = Path(args.out_dir)
            out.mkdir(parents=True, exist_ok=True)
            for name, schema in json_schemas().items():
                (out / f"{name}.schema.json").write_text(json.dumps(schema, indent=2) + "\n")
    except (NotCachedError, InsufficientWindowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (ValueError, TypeError, OSError) as exc:  # ValidationError, JSON errors are ValueErrors
        print(f"error: invalid input: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
