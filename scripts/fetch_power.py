"""Fetch NASA POWER daily point data for cached sites (network lives only in scripts/).

Usage: python scripts/fetch_power.py [site_id ...]   (default: every site in data/sites.json)

Per site, two requests (cached, so re-runs on the same day do not hit POWER again):
  main:  data/raw/power/<site>.json + data/power/<site>.csv
  IMERG: data/raw/power/<site>_imerg.json + data/power/<site>_imerg.csv
Raw files keep the full response with its header; CSVs have the header fill value as NaN.
"""
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from requests_cache import NEVER_EXPIRE, CachedSession
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

ROOT = Path(__file__).resolve().parents[1]
URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = ["PRECTOTCORR", "T2M_MIN", "T2M_MAX", "RH2M", "ALLSKY_SFC_SW_DWN", "GWETROOT"]
# IMERG precipitation is a separate request (own header, own files), the alternative to PRECTOTCORR
IMERG_PARAMETERS = ["IMERG_PRECTOT"]  # POWER serves IMERG in UTC only (LST request returns no data)
START = "19810101"
TIMEOUT = (5, 30)


def _retryable(exc: BaseException) -> bool:
    # Retry connection problems, timeouts, 429 and 5xx; never a 422 validation error.
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        code = exc.response.status_code
        return code == 429 or code >= 500
    return False


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10),
       retry=retry_if_exception(_retryable), reraise=True)
def _get(session: CachedSession, params: dict) -> requests.Response:
    resp = session.get(URL, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp


def to_table(body: dict) -> pd.DataFrame:
    """Daily table from a POWER response; the header's fill value becomes NaN."""
    df = pd.DataFrame(body["properties"]["parameter"])
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"
    return df.mask(df == body["header"]["fill_value"])


def bad_response(body: dict, df: pd.DataFrame) -> str | None:
    """Why a response must not replace the saved files, or None if it is usable."""
    if body.get("messages"):
        return f"POWER messages: {body['messages']}"
    empty = [c for c in df.columns if df[c].notna().sum() == 0]
    return f"no valid values for {empty}" if empty else None


def fetch_site(session: CachedSession, site: dict, end: str, parameters: list[str], suffix: str,
               extra: dict | None = None) -> None:
    params = {
        "parameters": ",".join(parameters), "community": "AG",
        "longitude": site["lon"], "latitude": site["lat"],
        "start": START, "end": end, "format": "JSON", **(extra or {}),
    }
    resp = _get(session, params)
    body = resp.json()
    df = to_table(body)  # check the new data before touching the files on disk
    problem = bad_response(body, df)
    if problem:
        raise SystemExit(f"{site['id']}{suffix}: not saved, existing files kept ({problem})")
    raw = {"request_url": resp.url, "accessed": date.today().isoformat(),
           "from_cache": getattr(resp, "from_cache", False), "response": body}
    (ROOT / "data/raw/power" / f"{site['id']}{suffix}.json").write_text(json.dumps(raw, indent=1))
    df.to_csv(ROOT / "data/power" / f"{site['id']}{suffix}.csv", float_format="%.4f")

    fill = body["header"]["fill_value"]
    print(f"{site['id']}{suffix}: {df.index[0].date()} .. {df.index[-1].date()} "
          f"({'cache' if raw['from_cache'] else 'live'}), fill_value={fill}")
    for col in df.columns:
        valid = df[col].dropna()
        first = valid.index[0].year if len(valid) else None
        print(f"  {col:18s} first valid year {first}, missing days {df[col].isna().sum()}")


def main(site_ids: list[str]) -> None:
    sites = json.loads((ROOT / "data/sites.json").read_text())["sites"]
    if site_ids:
        sites = [s for s in sites if s["id"] in site_ids]
    (ROOT / "cache").mkdir(exist_ok=True)
    session = CachedSession(str(ROOT / "cache/power"), backend="sqlite",
                            expire_after=NEVER_EXPIRE, stale_if_error=True)
    end = date.today().strftime("%Y%m%d")
    for site in sites:
        fetch_site(session, site, end, PARAMETERS, "")
        fetch_site(session, site, end, IMERG_PARAMETERS, "_imerg", {"time-standard": "UTC"})


if __name__ == "__main__":
    main(sys.argv[1:])
