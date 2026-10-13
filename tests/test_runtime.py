"""Resource, configuration, and saved-model regression checks."""

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import TypedDict

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.config import Settings
from backend.services import data_mapper, model_service
from tests.test_predict import VALID_PAYLOAD



class BaselineCase(TypedDict):
    """One recorded valid request, mapped row, and saved-model response."""

    payload: dict[str, str]
    columns: list[str]
    mapped: list[list[int | str]]
    response: model_service.PredictionResponse


ROOT = Path(__file__).resolve().parents[1]
BASELINES = json.loads((Path(__file__).parent / "fixtures/prediction_baseline.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", BASELINES)
def test_saved_model_baseline(case: BaselineCase) -> None:
    """Keep recorded pre-change model inputs and real prediction responses identical."""
    frame = data_mapper.prepare_model_frame(case["payload"])
    assert frame.columns.tolist() == case["columns"]
    assert frame.values.tolist() == case["mapped"]
    assert model_service.predict_probability(case["payload"]) == case["response"]
    with TestClient(app) as client:
        response = client.post("/predict", json=case["payload"])
    assert response.status_code == 200
    assert response.json() == case["response"]


def test_authoritative_mappings_and_model_order() -> None:
    """Use the tracked JSON codes and the same feature order as the saved model."""
    raw = json.loads(data_mapper.FEATURE_MAPPING_PATH.read_text(encoding="utf-8"))
    metadata = json.loads(model_service.METADATA_PATH.read_text(encoding="utf-8"))
    assert data_mapper.FEATURE_ORDER == metadata["features"]
    assert model_service._load_model()
    assert list(model_service._cached_model.feature_names_in_) == data_mapper.FEATURE_ORDER
    for field, mapping in raw.items():
        assert data_mapper.FEATURE_CONFIG[field]["mapping"] == mapping
        for key, code in mapping.items():
            mapped = data_mapper.prepare_model_input({**VALID_PAYLOAD, field: key})
            assert mapped[field] == code
            assert type(mapped[field]) is type(code)


@pytest.mark.parametrize("time,code", [("00:00", 1), ("08:00", 33), ("23:45", 96), (96, 96)])
def test_quarter_hour_boundaries(time: int | str, code: int) -> None:
    """Preserve the supported time boundaries and numeric time representation."""
    assert data_mapper.prepare_model_input({**VALID_PAYLOAD, "SHAA": time})["SHAA"] == code


@pytest.mark.parametrize("time", ["00:01", "24:00", "12:60", 0, 97])
def test_invalid_time_contract(time: int | str) -> None:
    """Reject unsupported time codes and non-quarter-hour strings."""
    with TestClient(app) as client:
        assert client.post("/predict", json={**VALID_PAYLOAD, "SHAA": time}).status_code == 422


def test_optional_environment_example() -> None:
    """Parse the actual example through pydantic-settings without changing local config."""
    settings = Settings(_env_file=ROOT / ".env.example")
    assert settings.cors_origins == ["http://127.0.0.1:8000", "http://localhost:8000"]
    assert not settings.debug
    assert "model_path" not in Settings.model_fields


def test_frontend_serving_and_cors() -> None:
    """Serve the actual UI assets and accept the configured local origin."""
    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Accident Severity Classifier" in page.text
        for asset in ["script.js?v=5", "style.css?v=5"]:
            response = client.get("/" + asset)
            assert response.status_code == 200
            assert response.content
        response = client.options("/predict", headers={
            "Origin": "http://127.0.0.1:8000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:8000"


@pytest.mark.parametrize("content", [None, "not a saved model"])
def test_unavailable_model_is_controlled(
    content: str | None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return HTTP 500 for missing or corrupt models without replacing the real artifact."""
    path = tmp_path / "model.joblib"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(model_service, "MODEL_PATH", path)
    monkeypatch.setattr(model_service, "_model_loaded", False)
    monkeypatch.setattr(model_service, "_cached_model", None)
    with TestClient(app) as client:
        response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert model_service._cached_model is None


@pytest.mark.parametrize("failure", ["missing", "unreadable", "malformed", "shape", "partial", "value"])
def test_mapping_failure_from_fresh_import(failure: str) -> None:
    """Start without usable mappings and return controlled errors instead of substitute codes."""
    # Redirect only the mapping read in an isolated interpreter; tracked files stay intact.
    code = '''
import io, json, sys
from pathlib import Path
from unittest.mock import patch
original_open = Path.open
failure = sys.argv[1]
def resource_open(path: Path, *args: object, **kwargs: object) -> object:
    """Inject a mapping read failure while leaving other resources unchanged."""
    if path.name == "feature_value_mappings.json":
        if failure == "missing": raise FileNotFoundError("test mapping missing")
        if failure == "unreadable": raise PermissionError("test mapping unreadable")
        if failure == "malformed": return io.StringIO("{")
        if failure == "shape": return io.StringIO("[]")
        if failure == "partial": return io.StringIO('{"NAFA":{"unknown":0}}')
        with original_open(path, *args, **kwargs) as handle: payload = json.load(handle)
        payload["NAFA"]["unknown"] = []
        return io.StringIO(json.dumps(payload))
    return original_open(path, *args, **kwargs)
with patch.object(Path, "open", resource_open):
    from backend.app import app
    from backend.services import data_mapper
from fastapi.testclient import TestClient
assert data_mapper._FEATURE_MAPPING_DB is None
assert not data_mapper.ROAD_STRUCTURE_MAPPING
with TestClient(app) as client:
    assert client.get("/").status_code == 200
    response = client.post("/predict", json=json.loads(sys.argv[2]))
    assert response.status_code == 500, response.text
    assert response.json() == {"detail":"Internal server error"}
print("controlled mapping failure")
'''
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, failure, json.dumps(VALID_PAYLOAD)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "controlled mapping failure" in result.stdout
