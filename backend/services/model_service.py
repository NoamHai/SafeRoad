from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TypedDict, TYPE_CHECKING

import joblib
import pandas as pd

if TYPE_CHECKING:
    from sklearn.pipeline import Pipeline

from .data_mapper import FEATURE_ORDER, prepare_model_frame


class PredictionResponse(TypedDict):
    """The unchanged four-field prediction response."""

    prediction: int
    prediction_label: str
    light_probability: float
    dangerous_probability: float


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "safe_roads_ml" / "final_model" / "saved_model"
MODEL_PATH = MODEL_DIR / "safe_roads_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

_cached_model: Pipeline | None = None
_cached_metadata: Optional[Dict[str, Any]] = None
_model_loaded = False


def _load_metadata() -> Dict[str, Any]:
    """Load and cache the model metadata JSON."""
    global _cached_metadata
    if _cached_metadata is not None:
        return _cached_metadata

    if METADATA_PATH.exists():
        try:
            with METADATA_PATH.open("r", encoding="utf-8") as handle:
                _cached_metadata = json.load(handle)
                return _cached_metadata
        except Exception as exc:
            logger.warning("Failed to load model metadata: %s", exc)

    _cached_metadata = {}
    return _cached_metadata


def _load_model() -> bool:
    """Load the final saved model once per process."""
    global _cached_model, _model_loaded
    if _model_loaded:
        return _cached_model is not None

    if MODEL_PATH.exists():
        try:
            _cached_model = joblib.load(MODEL_PATH)
            logger.info("Loaded final model from %s", MODEL_PATH)
        except Exception as exc:
            logger.warning("Failed to load final model from %s: %s", MODEL_PATH, exc)
            _cached_model = None
    else:
        logger.warning("Final model file not found at %s; predictions are disabled", MODEL_PATH)
        _cached_model = None

    _model_loaded = True
    return _cached_model is not None


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Clamp a value to the [minimum, maximum] range."""
    return max(minimum, min(maximum, value))


def _target_labels() -> Dict[int, str]:
    """Return the {0: light, 1: dangerous} label map from metadata."""
    metadata = _load_metadata()
    target_meaning = metadata.get("target_meaning", {}) if isinstance(metadata, dict) else {}
    return {
        0: str(target_meaning.get("0", "Light accident")),
        1: str(target_meaning.get("1", "Dangerous accident")),
    }


def _final_feature_frame(user_input: Dict[str, object]) -> pd.DataFrame:
    """Build the single-row model input frame from user input."""
    missing = [feature for feature in FEATURE_ORDER if feature not in user_input]
    unexpected = sorted(set(user_input).difference(FEATURE_ORDER))
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing required fields: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected fields: {', '.join(unexpected)}")
        raise ValueError("Invalid prediction payload; " + "; ".join(details))

    return prepare_model_frame(user_input, FEATURE_ORDER)


def _probabilities_from_model(model: Pipeline, frame: pd.DataFrame) -> Tuple[int, float, float]:
    """Return (prediction, light_prob, dangerous_prob) from the model's predict_proba."""
    raw_probabilities = model.predict_proba(frame)[0]
    # Probability columns follow model.classes_, not a fixed positional label order.
    classes = list(getattr(model, "classes_", [0, 1]))
    probability_map = {int(cls): float(prob) for cls, prob in zip(classes, raw_probabilities)}

    dangerous_probability = probability_map.get(1)
    light_probability = probability_map.get(0)

    if dangerous_probability is None or light_probability is None:
        if len(raw_probabilities) >= 2:
            light_probability = float(raw_probabilities[0])
            dangerous_probability = float(raw_probabilities[-1])
        else:
            dangerous_probability = float(raw_probabilities[0])
            light_probability = 1.0 - dangerous_probability

    dangerous_probability = _clamp(float(dangerous_probability))
    light_probability = _clamp(float(light_probability))
    prediction = 1 if dangerous_probability >= light_probability else 0
    return prediction, light_probability, dangerous_probability


def _prediction_response(prediction: int, light_probability: float, dangerous_probability: float) -> PredictionResponse:
    """Build the API response dict from a prediction and its probabilities."""
    labels = _target_labels()
    return {
        "prediction": int(prediction),
        "prediction_label": labels.get(int(prediction), labels[1 if prediction else 0]),
        "light_probability": round(float(light_probability), 4),
        "dangerous_probability": round(float(dangerous_probability), 4),
    }


def predict_probability(user_input: Dict[str, object]) -> PredictionResponse:
    """Predict the binary accident class for the final 16-feature payload."""

    frame = _final_feature_frame(dict(user_input))
    # Require the trained model; there is no fallback — fail loudly if it is missing.
    if not _load_model() or _cached_model is None:
        logger.error("Final model not available at %s; prediction disabled", MODEL_PATH)
        raise RuntimeError("Final model not available; prediction disabled")

    prediction, light_probability, dangerous_probability = _probabilities_from_model(_cached_model, frame)
    return _prediction_response(prediction, light_probability, dangerous_probability)
