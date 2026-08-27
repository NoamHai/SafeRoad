"""
Tests for the current POST /predict API contract.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.services.data_mapper import FEATURE_ORDER, prepare_model_input
from backend.services.model_service import predict_probability


client = TestClient(app)

VALID_PAYLOAD = {
    "SHAA": "08:00",
    "HODESH_TEUNA": "january",
    "YOM_BASHAVUA": "sunday",
    "SUG_TEUNA": "front_to_side_collision",
    "ROAD_STRUCTURE": "single_lane_1",
    "ROHAV": "5_to_7_meters",
    "NAFA": "tel_aviv",
    "ZURAT_ISHUV": "jewish_city_100k_200k",
    "MEHIRUT_MUTERET": "up_to_50_kmh",
    "TEURA": "daylight",
    "SUG_DEREH": "urban_intersection",
    "SIMUN_TIMRUR": "no_defect",
    "TKINUT": "no_defect",
    "PNE_KVISH": "dry",
    "MEZEG_AVIR": "clear",
    "YOM_LAYLA": "day",
}

EXPECTED_RESPONSE_KEYS = {
    "prediction",
    "prediction_label",
    "light_probability",
    "dangerous_probability",
}

LEGACY_PAYLOAD = {
    "road_type": "urban",
    "weather": "clear",
    "time_of_day": "day",
    "lighting": "daylight",
    "junction": "no_junction",
    "road_surface": "dry",
}


def test_valid_payload_matches_current_feature_contract() -> None:
    """The test payload should stay aligned with the mapper's current 16 features."""
    assert list(VALID_PAYLOAD) == FEATURE_ORDER

    model_input = prepare_model_input(VALID_PAYLOAD)

    assert set(model_input) == set(FEATURE_ORDER)
    assert model_input["SHAA"] == 33
    assert model_input["HODESH_TEUNA"] == 1
    assert model_input["SUG_DEREH"] == 1


def test_post_predict_successful_prediction() -> None:
    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in {0, 1}
    assert body["prediction_label"] in {"Light accident", "Dangerous accident"}


def test_post_predict_response_structure_and_types() -> None:
    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == EXPECTED_RESPONSE_KEYS
    assert isinstance(body["prediction"], int)
    assert isinstance(body["prediction_label"], str)
    assert isinstance(body["light_probability"], float)
    assert isinstance(body["dangerous_probability"], float)


def test_post_predict_probability_values_are_valid() -> None:
    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    light_probability = body["light_probability"]
    dangerous_probability = body["dangerous_probability"]

    assert 0.0 <= light_probability <= 1.0
    assert 0.0 <= dangerous_probability <= 1.0
    assert light_probability + dangerous_probability == pytest.approx(1.0, abs=0.01)
    assert body["prediction"] == (1 if dangerous_probability >= light_probability else 0)


def test_post_predict_missing_required_field_is_rejected() -> None:
    payload = VALID_PAYLOAD.copy()
    payload.pop("SHAA")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert "SHAA" in response.text


def test_post_predict_legacy_payload_is_rejected() -> None:
    response = client.post("/predict", json=LEGACY_PAYLOAD)

    assert response.status_code == 422
    assert "road_type" in response.text
    assert "SHAA" in response.text


@pytest.mark.parametrize(
    "legacy_fields",
    [
        {"weather": "clear"},
        {"road_type": "urban", "junction": "no_junction"},
    ],
)
def test_post_predict_partial_legacy_payload_is_rejected(legacy_fields: dict[str, str]) -> None:
    response = client.post("/predict", json=legacy_fields)

    assert response.status_code == 422
    assert next(iter(legacy_fields)) in response.text


def test_post_predict_mixed_legacy_and_current_payload_is_rejected() -> None:
    response = client.post("/predict", json={**VALID_PAYLOAD, "weather": "clear"})

    assert response.status_code == 422
    assert "weather" in response.text


def test_predict_probability_does_not_default_missing_required_fields() -> None:
    incomplete_payload = VALID_PAYLOAD.copy()
    incomplete_payload.pop("ROHAV")

    with pytest.raises(ValueError, match="missing required fields: ROHAV"):
        predict_probability(incomplete_payload)


def test_predict_probability_rejects_legacy_fields_before_inference() -> None:
    expected = "unexpected fields: junction, lighting, road_surface, road_type, time_of_day, weather"
    with pytest.raises(ValueError, match=expected):
        predict_probability(LEGACY_PAYLOAD)


def test_post_predict_invalid_shaa_is_rejected() -> None:
    payload = {**VALID_PAYLOAD, "SHAA": "25:00"}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert "SHAA" in response.json()["detail"]


def test_post_predict_model_value_error_becomes_422(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_value_error(payload: dict[str, object]) -> dict[str, object]:
        raise ValueError("bad mapped value")

    monkeypatch.setattr("backend.routes.predict.predict_probability", raise_value_error)

    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 422
    assert response.json()["detail"] == "bad mapped value"


def test_post_predict_unexpected_model_error_becomes_500(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_runtime_error(payload: dict[str, object]) -> dict[str, object]:
        raise RuntimeError("model unavailable")

    monkeypatch.setattr("backend.routes.predict.predict_probability", raise_runtime_error)

    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
