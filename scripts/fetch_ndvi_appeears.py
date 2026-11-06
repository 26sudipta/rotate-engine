"""Download a finished AppEEARS task bundle into data/ndvi/ (network lives only in scripts/).

Usage: python scripts/fetch_ndvi_appeears.py [task_id] [subdir]   (subdir e.g. "hls" -> data/ndvi/hls/)
Reads EARTHDATA_USERNAME / EARTHDATA_PASSWORD from the environment or .env (never committed).
Writes every bundle file to data/ndvi/ and data/ndvi/bundle_manifest.json (file names + sha256).
"""
import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
API = "https://appeears.earthdatacloud.nasa.gov/api"
DEFAULT_TASK = "dfdede24-460a-454b-bdcf-b4c52f397bf8"  # rotate_ndvi_2sites, submitted 5 Nov 2026
TIMEOUT = (5, 120)


def credentials() -> tuple[str, str]:
    env = dict(os.environ)
    dotenv = ROOT / ".env"
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                env.setdefault(key.strip(), value.strip().strip("'\""))
    user, password = env.get("EARTHDATA_USERNAME"), env.get("EARTHDATA_PASSWORD")
    if not user or not password:
        sys.exit("Set EARTHDATA_USERNAME and EARTHDATA_PASSWORD in .env (see .env.example)")
    return user, password


def strip_user(request_json: bytes) -> bytes:
    """Drop the Earthdata user id (an email address) before the file can reach the public repo."""
    data = json.loads(request_json)
    data.pop("user_id", None)
    return json.dumps(data).encode()


def build_manifest(task_id: str, files: list[dict], downloaded: date) -> dict:
    """The manifest shape rotate_engine.provenance reads."""
    return {"task_id": task_id, "route": "appeears", "downloaded": downloaded.isoformat(),
            "files": files}


def main(task_id: str, subdir: str = "") -> None:
    login = requests.post(f"{API}/login", auth=credentials(), timeout=TIMEOUT)
    login.raise_for_status()
    headers = {"Authorization": f"Bearer {login.json()['token']}"}  # token stays in memory only

    status = requests.get(f"{API}/task/{task_id}", headers=headers, timeout=TIMEOUT)
    status.raise_for_status()
    if status.json().get("status") != "done":
        sys.exit(f"task {task_id} is '{status.json().get('status')}', not done; try later")

    bundle = requests.get(f"{API}/bundle/{task_id}", headers=headers, timeout=TIMEOUT)
    bundle.raise_for_status()
    if subdir and not subdir.isalnum():
        sys.exit("subdir must be a plain folder name such as 'hls'")
    out = ROOT / "data" / "ndvi" / subdir  # a subdir keeps the MOD13Q1 bundle and manifest untouched
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for f in bundle.json()["files"]:
        resp = requests.get(f"{API}/bundle/{task_id}/{f['file_id']}", headers=headers,
                            timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        name = Path(f["file_name"]).name  # flatten any sub-folder; never write outside data/ndvi/
        content = resp.content
        if f.get("sha256") and f["sha256"] != hashlib.sha256(content).hexdigest():
            sys.exit(f"sha256 mismatch for {name}")
        if name.endswith("-request.json"):
            content = strip_user(content)
        (out / name).write_bytes(content)
        manifest.append({"file_name": name, "sha256": hashlib.sha256(content).hexdigest()})
        print(f"saved {(out / name).relative_to(ROOT)} ({len(content)} bytes)")
    (out / "bundle_manifest.json").write_text(json.dumps(
        build_manifest(task_id, manifest, date.today()), indent=2) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TASK, sys.argv[2] if len(sys.argv) > 2 else "")
