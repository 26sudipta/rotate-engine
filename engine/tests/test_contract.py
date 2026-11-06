import json
from pathlib import Path

import jsonschema
import pytest

from rotate_engine.io import root
from rotate_engine.models import BacktestResult, CardSet, NdviSeries, NdviYears, json_schemas

FIXTURES = sorted((root() / "fixtures").glob("*.json"))
SCHEMAS = root() / "schemas"


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_fixtures_match_schema(path: Path) -> None:
    data = json.loads(path.read_text())
    model, name = ((BacktestResult, "backtest_result") if path.name.startswith("backtest_")
                   else (NdviYears, "ndvi_years") if path.name.startswith("ndvi_years_")
                   else (NdviSeries, "ndvi_series") if path.name.startswith("ndvi_")
                   else (CardSet, "card_set"))
    jsonschema.validate(data, json.loads((SCHEMAS / f"{name}.schema.json").read_text()))
    model.model_validate(data)


def test_committed_schemas_are_current() -> None:
    for name, schema in json_schemas().items():
        assert json.loads((SCHEMAS / f"{name}.schema.json").read_text()) == schema, name


def test_schema_version_is_required() -> None:
    data = json.loads((root() / "fixtures" / "cards_ctg.json").read_text())
    del data["schema_version"]
    schema = json.loads((SCHEMAS / "card_set.schema.json").read_text())
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, schema)


def test_unknown_field_and_bad_tag_rejected() -> None:
    data = json.loads((root() / "fixtures" / "cards_ctg.json").read_text())
    schema = json.loads((SCHEMAS / "card_set.schema.json").read_text())
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**data, "extra": 1}, schema)
    data["cards"][0]["evidence"][0]["tag"] = "NASA"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, schema)
