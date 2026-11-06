"""File access only: data/sites.json, data/power/, data/raw/power/, rules/. Never the network."""
import json
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd


class NotCachedError(LookupError):
    """The requested site has no cached data."""


def root() -> Path:
    """Repo root holding data/ and rules/. ROTATE_ROOT overrides the search up from this file."""
    env = os.environ.get("ROTATE_ROOT")
    if env:
        return Path(env)
    for parent in Path(__file__).resolve().parents:
        if (parent / "data" / "sites.json").exists():
            return parent
    raise FileNotFoundError("data/sites.json not found; set ROTATE_ROOT to the repo root")


def load_sites() -> list[dict]:
    return json.loads((root() / "data" / "sites.json").read_text())["sites"]


def get_site(site_id: str) -> dict:
    for site in load_sites():
        if site["id"] == site_id:
            return site
    raise NotCachedError(f"site '{site_id}' is not in data/sites.json")


def load_power(site_id: str) -> pd.DataFrame:
    """Daily POWER table indexed by date. The fetch script already turned fill values into NaN."""
    path = root() / "data" / "power" / f"{site_id}.csv"
    if not path.exists():
        raise NotCachedError(f"no cached POWER data for '{site_id}'")
    df = pd.read_csv(path, index_col="date", parse_dates=["date"])
    fill = power_header(site_id)["fill_value"]
    return df.mask(df == fill)  # defensive: a hand-made CSV may still carry the fill value


def load_imerg(site_id: str) -> pd.Series:
    """Daily GPM IMERG precipitation (mm/day, UTC) as served by POWER; fill values already NaN."""
    path = root() / "data" / "power" / f"{site_id}_imerg.csv"
    if not path.exists():
        raise NotCachedError(f"no cached IMERG rain for '{site_id}'")
    rain = pd.read_csv(path, index_col="date", parse_dates=["date"])["IMERG_PRECTOT"]
    return rain.mask(rain == power_header(site_id)["fill_value"])


@lru_cache(maxsize=32)
def _parse_json(path: Path, mtime_ns: int) -> dict:
    return json.loads(path.read_text())


def read_json(path: Path) -> dict:
    """Parsed JSON file, re-read whenever it changes on disk, so a long-running backend
    picks up a POWER refetch or a rules.json edit without a restart."""
    return _parse_json(path, path.stat().st_mtime_ns)


def _raw_power(site_id: str) -> dict:
    path = root() / "data" / "raw" / "power" / f"{site_id}.json"
    if not path.exists():
        raise NotCachedError(f"no raw POWER response for '{site_id}'")
    return read_json(path)


def power_header(site_id: str) -> dict:
    return _raw_power(site_id)["response"]["header"]


def power_provenance_raw(site_id: str) -> dict:
    raw = _raw_power(site_id)
    return {"request_url": raw["request_url"], "accessed": raw["accessed"],
            "header": raw["response"]["header"],
            "parameters": list(raw["response"]["parameters"])}


def load_ndvi_raw() -> pd.DataFrame:
    """The AppEEARS point-results CSV in data/ndvi/ (all sites in one file)."""
    files = sorted((root() / "data" / "ndvi").glob("*-MOD13Q1-061-results.csv"))
    if not files:
        raise NotCachedError("NDVI pending: no AppEEARS results CSV in data/ndvi/")
    return pd.read_csv(files[-1])


def load_ornl(site_id: str, product: str, km: int) -> pd.DataFrame:
    """An ORNL subset file written by scripts/fetch_ndvi_ornl.py (raw integers, one row per date and band)."""
    path = root() / "data" / "ndvi" / "ornl" / f"{site_id}_{product}_{km}km.csv"
    if not path.exists():
        raise NotCachedError(f"no ORNL {product} file for '{site_id}': run scripts/fetch_ndvi_ornl.py")
    return pd.read_csv(path)


def load_hls(product: str) -> pd.DataFrame:
    """One AppEEARS HLS point-results CSV in data/ndvi/hls/, e.g. product "HLSS30-VI-020" or "HLSS30-020"."""
    files = sorted((root() / "data" / "ndvi" / "hls").glob(f"*-{product}-results.csv"))
    if not files:
        raise NotCachedError(f"HLS pending: no {product} results CSV in data/ndvi/hls/")
    return pd.read_csv(files[-1])


def ndvi_manifest() -> dict | None:
    path = root() / "data" / "ndvi" / "bundle_manifest.json"
    return json.loads(path.read_text()) if path.exists() else None
