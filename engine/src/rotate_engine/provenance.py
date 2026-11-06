"""Provenance and source wording, built from the saved POWER response header (never hard-coded)."""
from urllib.parse import parse_qs, urlparse

from .io import ndvi_manifest, power_provenance_raw
from .models import NdviProvenance, PowerProvenance, Provenance

NDVI_LAYERS = ["_250m_16_days_NDVI", "_250m_16_days_pixel_reliability", "_250m_16_days_VI_Quality",
               "_250m_16_days_composite_day_of_the_year"]


def power_provenance(site_id: str) -> PowerProvenance:
    raw = power_provenance_raw(site_id)
    query = parse_qs(urlparse(raw["request_url"]).query)
    return PowerProvenance(
        endpoint=raw["request_url"], parameters=raw["parameters"],
        community=query.get("community", ["?"])[0], accessed=raw["accessed"],
        api_version=raw["header"]["api"]["version"], header_sources=raw["header"]["sources"],
        fill_value=raw["header"]["fill_value"])


def ndvi_provenance() -> NdviProvenance | None:
    m = ndvi_manifest()
    if m is None:
        return None
    results = next((f["sha256"] for f in m["files"] if f["file_name"].endswith("-results.csv")), None)
    return NdviProvenance(product="MOD13Q1.061", layers=NDVI_LAYERS, route=m["route"],
                          task_id=m["task_id"], accessed=m["downloaded"], sha256=results)


def provenance(site_id: str) -> Provenance:
    return Provenance(power=power_provenance(site_id), ndvi=ndvi_provenance())


def power_source_label(p: PowerProvenance, parameter: str) -> str:
    return (f"NASA POWER daily {parameter}, API {p.api_version}; sources listed in the response "
            f"header: {', '.join(p.header_sources)}. Reanalysis/model output, not field measurement.")


def power_warnings(p: PowerProvenance) -> list[str]:
    return [f"The most recent days come from POWER's near-real-time products, not the long-term "
            f"reanalysis; the response header lists these sources: {', '.join(p.header_sources)}."]
