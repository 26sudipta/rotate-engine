"""Submit one AppEEARS point task for HLS 30 m NDVI at every cached site (network lives only in scripts/).

Usage: python scripts/submit_ndvi_hls.py
Needs EARTHDATA_USERNAME / EARTHDATA_PASSWORD in .env. Prints the task_id. When the task is done:
    python scripts/fetch_ndvi_appeears.py <task_id> hls     (writes data/ndvi/hls/)
Layers: NDVI from HLSS30_VI.020 (Sentinel-2) and HLSL30_VI.020 (Landsat), plus Fmask (cloud/shadow
mask) from HLSS30.020 and HLSL30.020: the VI products carry no QA layer of their own.
"""
import json
from datetime import date
from pathlib import Path

import requests

from fetch_ndvi_appeears import API, TIMEOUT, credentials

ROOT = Path(__file__).resolve().parents[1]
START = "11-01-2015"  # HLSS30 starts 28 Nov 2015; covers the Boro seasons 2016 on
LAYERS = [{"product": p, "layer": l} for p, l in (
    ("HLSS30_VI.020", "NDVI"), ("HLSL30_VI.020", "NDVI"), ("HLSS30.020", "Fmask"), ("HLSL30.020", "Fmask"))]


def task(sites: list[dict], end: date) -> dict:
    return {"task_type": "point", "task_name": "rotate_hls_2sites",
            "params": {"dates": [{"startDate": START, "endDate": end.strftime("%m-%d-%Y")}],
                       "layers": LAYERS,
                       "coordinates": [{"id": s["id"], "latitude": s["lat"], "longitude": s["lon"]}
                                       for s in sites]}}


def main() -> None:
    sites = json.loads((ROOT / "data/sites.json").read_text())["sites"]
    login = requests.post(f"{API}/login", auth=credentials(), timeout=TIMEOUT)
    login.raise_for_status()
    headers = {"Authorization": f"Bearer {login.json()['token']}"}  # token stays in memory only
    resp = requests.post(f"{API}/task", json=task(sites, date.today()), headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    print(f"submitted: task_id {resp.json()['task_id']} (status {resp.json().get('status')})")


if __name__ == "__main__":
    main()
