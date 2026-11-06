"""Fetch MODIS NDVI subsets from the ORNL DAAC web service (no login; network lives only in scripts/).

Usage: python scripts/fetch_ndvi_ornl.py [site_id ...]   (default: every site in data/sites.json)

Two jobs per site (responses cached in cache/ornl, so re-runs don't hit ORNL again):
  MYD13Q1 (Aqua), centre pixel, whole record: NDVI, pixel reliability, composite day of year.
      Interleaved with the Terra (MOD13Q1, AppEEARS) curve for display only.
  MOD13Q1 (Terra), 9x9-pixel window (1 km each way), from WINDOW_FROM: NDVI and pixel reliability.
      The engine summarises the central 3x3 pixels to show how much neighbouring pixels differ.
Writes data/ndvi/ornl/<site>_<product>_<km>km.csv (raw integers, one row per date and band, pixel
values p0..pN row by row from the upper left) and data/ndvi/ornl/manifest.json (sha256 per file).
"""
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from requests_cache import NEVER_EXPIRE, CachedSession
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

ROOT = Path(__file__).resolve().parents[1]
API = "https://modis.ornl.gov/rst/api/v1"
OUT = ROOT / "data" / "ndvi" / "ornl"
TIMEOUT = (10, 120)
DATES_PER_CALL = 10  # the service's limit
WORKERS = 3  # polite: a 9x9 call takes ~30 s server-side
B = "250m_16_days_"
# shortcut: the window covers recent seasons only (a full-record 9x9 pull is ~2 h of ORNL time);
# move WINDOW_FROM back if the team wants the window for every analog year.
WINDOW_FROM = "2023-11-01"
JOBS = [  # (product, km above/below and left/right, bands, first calendar date or None)
    ("MYD13Q1", 0, [B + "NDVI", B + "pixel_reliability", B + "composite_day_of_the_year"], None),
    ("MOD13Q1", 1, [B + "NDVI", B + "pixel_reliability"], WINDOW_FROM),
]


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, max=30),
       retry=retry_if_exception(_retryable), reraise=True)
def _get(session: CachedSession, path: str, params: dict) -> dict:
    resp = session.get(f"{API}/{path}", params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def subset(session: CachedSession, site: dict, product: str, km: int, band: str, chunk: list[dict]) -> dict:
    body = _get(session, f"{product}/subset", {
        "latitude": site["lat"], "longitude": site["lon"], "band": band, "kmAboveBelow": km,
        "kmLeftRight": km, "startDate": chunk[0]["modis_date"], "endDate": chunk[-1]["modis_date"]})
    n = int(body["nrows"]) * int(body["ncols"])
    side = 2 * km + 1
    if int(body["nrows"]) < side or any(len(s["data"]) != n for s in body["subset"]):
        raise SystemExit(f"{site['id']} {product} {band}: unexpected grid {body['nrows']}x{body['ncols']}")
    return body


def fetch_job(session: CachedSession, site: dict, product: str, km: int, bands: list[str],
              first: str | None) -> tuple[Path, dict]:
    dates = _get(session, f"{product}/dates", {"latitude": site["lat"], "longitude": site["lon"]})["dates"]
    if first:
        dates = [d for d in dates if d["calendar_date"] >= first]
    chunks = [dates[i:i + DATES_PER_CALL] for i in range(0, len(dates), DATES_PER_CALL)]
    calls = [(band, c) for band in bands for c in chunks]
    print(f"{site['id']} {product} km={km}: {len(dates)} dates, {len(calls)} calls", flush=True)
    with ThreadPoolExecutor(WORKERS) as pool:
        bodies = list(pool.map(lambda bc: subset(session, site, product, km, *bc), calls))
    rows = [{"calendar_date": s["calendar_date"], "modis_date": s["modis_date"], "band": s["band"],
             **{f"p{i}": v for i, v in enumerate(s["data"])}}
            for body in bodies for s in body["subset"]]
    table = pd.DataFrame(rows).drop_duplicates(["calendar_date", "band"]).sort_values(["band", "calendar_date"])
    if table.empty:
        raise SystemExit(f"{site['id']} {product}: no data returned, nothing saved")
    path = OUT / f"{site['id']}_{product}_{km}km.csv"
    path.write_text(table.to_csv(index=False))
    meta = {k: bodies[0][k] for k in ("nrows", "ncols", "cellsize", "xllcorner", "yllcorner")}
    print(f"  saved {path.relative_to(ROOT)}: {table['calendar_date'].min()} .. {table['calendar_date'].max()}")
    return path, {"product": product, "km": km, "bands": bands, "first": first, **meta}


def main(site_ids: list[str]) -> None:
    sites = json.loads((ROOT / "data/sites.json").read_text())["sites"]
    if site_ids:
        sites = [s for s in sites if s["id"] in site_ids]
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT / "cache").mkdir(exist_ok=True)
    session = CachedSession(str(ROOT / "cache/ornl"), backend="sqlite", expire_after=NEVER_EXPIRE,
                            stale_if_error=True)
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"files": {}}
    for site in sites:
        for product, km, bands, first in JOBS:
            path, meta = fetch_job(session, site, product, km, bands, first)
            manifest["files"][path.name] = {
                "site_id": site["id"], "lat": site["lat"], "lon": site["lon"], **meta,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest.update(route="ornl", service=API, accessed=date.today().isoformat())
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
