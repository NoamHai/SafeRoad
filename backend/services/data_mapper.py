"""Map application selections to model codes and retain legacy analysis helpers."""

from pathlib import Path
from typing import Dict, Optional, List, TypedDict
import json
import re

import pandas as pd
import numpy as np

ModelCode = int | str | float | np.integer


class FeatureEntry(TypedDict):
    """One authoritative feature mapping and its English description."""

    mapping: dict[str, int | str]
    description: str


class MappingDatabase(TypedDict):
    """The loaded mapping resource in the form used by conversion helpers."""

    feature_order: list[str]
    features: dict[str, FeatureEntry]


class ValidationReport(TypedDict):
    """Warnings and errors reported by the standalone validation helper."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    missing_features: list[str]


# Feature mappings: frontend option keys → raw model values
FEATURE_MAPPING_PATH = Path(__file__).with_name("feature_value_mappings.json")

DEFAULT_FEATURE_ORDER = [
    "SHAA",
    "HODESH_TEUNA",
    "YOM_BASHAVUA",
    "SUG_TEUNA",
    "ROAD_STRUCTURE",
    "ROHAV",
    "NAFA",
    "ZURAT_ISHUV",
    "MEHIRUT_MUTERET",
    "TEURA",
    "SUG_DEREH",
    "SIMUN_TIMRUR",
    "TKINUT",
    "PNE_KVISH",
    "MEZEG_AVIR",
    "YOM_LAYLA",
]


def _load_feature_mapping_db() -> MappingDatabase:
    """Load the required authoritative mappings without substituting older codes."""
    try:
        with FEATURE_MAPPING_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict) or set(payload) != set(DEFAULT_FEATURE_ORDER) - {"SHAA"}:
            raise ValueError("Expected mappings for the 15 categorical fields; SHAA is converted separately")
        if any(
            not isinstance(mapping, dict) or not mapping
            or any(not isinstance(value, (int, str)) for value in mapping.values())
            for mapping in payload.values()
        ):
            raise ValueError("Expected nonempty feature mappings with integer or string codes")
        return {
            "feature_order": list(DEFAULT_FEATURE_ORDER),
            "features": {
                name: {"mapping": mapping, "description": name.replace("_", " ").title()}
                for name, mapping in payload.items()
            },
        }
    except (OSError, ValueError) as exc:
        raise RuntimeError("Authoritative feature mappings are unavailable or invalid") from exc


# Keep static serving available; prediction reports resource errors through the route.
try:
    _FEATURE_MAPPING_DB = _load_feature_mapping_db()
except RuntimeError:
    _FEATURE_MAPPING_DB = None
FEATURE_ORDER = list(DEFAULT_FEATURE_ORDER)


def _mapping_for(feature_name: str) -> Dict[str, int | str]:
    """Return authoritative codes, or an empty mapping when the resource failed."""
    if _FEATURE_MAPPING_DB is None:
        return {}
    feature_entry = _FEATURE_MAPPING_DB["features"][feature_name]
    return {str(key): value for key, value in feature_entry["mapping"].items()}


def _shaa_mapping() -> Dict[str, int]:
    """Build the SHAA time mapping: 'HH:MM' → 1..96 (15-minute slots)."""
    return {
        f"{hour:02d}:{minute:02d}": (hour * 4) + (minute // 15) + 1
        for hour in range(24)
        for minute in (0, 15, 30, 45)
    }


SPEED_LIMIT_MAPPING = _mapping_for("MEHIRUT_MUTERET")
ROAD_TYPE_MAPPING = _mapping_for("SUG_DEREH")
ROAD_SURFACE_MAPPING = _mapping_for("PNE_KVISH")
ACCIDENT_TYPE_MAPPING = _mapping_for("SUG_TEUNA")
HOUR_MAPPING = _shaa_mapping()
MONTH_MAPPING = _mapping_for("HODESH_TEUNA")
DAY_OF_WEEK_MAPPING = _mapping_for("YOM_BASHAVUA")
LIGHTING_MAPPING = _mapping_for("TEURA")
SETTLEMENT_MAPPING = _mapping_for("ZURAT_ISHUV")
TRAFFIC_SIGNAL_MAPPING = _mapping_for("SIMUN_TIMRUR")
ROAD_CONDITION_MAPPING = _mapping_for("TKINUT")
ROAD_WIDTH_MAPPING = _mapping_for("ROHAV")
DISTRICT_MAPPING = _mapping_for("NAFA")
WEATHER_MAPPING = _mapping_for("MEZEG_AVIR")
DAY_NIGHT_MAPPING = _mapping_for("YOM_LAYLA")
ROAD_STRUCTURE_MAPPING = _mapping_for("ROAD_STRUCTURE")


# Reverse mappings: model codes to frontend option keys (for analysis tools).
REVERSE_MAPPINGS = {
    "MEHIRUT_MUTERET": {v: k for k, v in SPEED_LIMIT_MAPPING.items()},
    "SUG_DEREH": {v: k for k, v in ROAD_TYPE_MAPPING.items()},
    "PNE_KVISH": {v: k for k, v in ROAD_SURFACE_MAPPING.items()},
    "SUG_TEUNA": {v: k for k, v in ACCIDENT_TYPE_MAPPING.items()},
    "SHAA": {v: k for k, v in HOUR_MAPPING.items()},
    "HODESH_TEUNA": {v: k for k, v in MONTH_MAPPING.items()},
    "YOM_BASHAVUA": {v: k for k, v in DAY_OF_WEEK_MAPPING.items()},
    "TEURA": {v: k for k, v in LIGHTING_MAPPING.items()},
    "ZURAT_ISHUV": {v: k for k, v in SETTLEMENT_MAPPING.items()},
    "SIMUN_TIMRUR": {v: k for k, v in TRAFFIC_SIGNAL_MAPPING.items()},
    "TKINUT": {v: k for k, v in ROAD_CONDITION_MAPPING.items()},
    "ROHAV": {v: k for k, v in ROAD_WIDTH_MAPPING.items()},
    "NAFA": {v: k for k, v in DISTRICT_MAPPING.items()},
    "MEZEG_AVIR": {v: k for k, v in WEATHER_MAPPING.items()},
    "YOM_LAYLA": {v: k for k, v in DAY_NIGHT_MAPPING.items()},
    "ROAD_STRUCTURE": {v: k for k, v in ROAD_STRUCTURE_MAPPING.items()},
}


# Feature field configuration
FEATURE_CONFIG = {}
for feature_name in FEATURE_ORDER:
    FEATURE_CONFIG[feature_name] = {
        "type": "integer" if feature_name in {"SHAA", "HODESH_TEUNA", "YOM_BASHAVUA"} else "categorical",
        "mapping": HOUR_MAPPING if feature_name == "SHAA" else _mapping_for(feature_name),
        "default": 0,
        "description": feature_name.replace("_", " ").title(),
    }


# Core conversion functions

def _normalize_key(value: object) -> str:
    """Normalize a key to a trimmed lowercase string for matching."""
    return str(value).strip().lower()


def _coerce_shaa(value: object) -> int:
    """Coerce a SHAA value (int 1..96 or 'HH:MM') to its 1..96 time code."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise ValueError("Field 'SHAA' is required")

    if isinstance(value, (int, np.integer)):
        int_value = int(value)
        if 1 <= int_value <= 96:
            return int_value
        raise ValueError("Field 'SHAA' must be in range 1..96")

    if isinstance(value, float) and value.is_integer():
        int_value = int(value)
        if 1 <= int_value <= 96:
            return int_value
        raise ValueError("Field 'SHAA' must be in range 1..96")

    text = str(value).strip()
    if text.isdigit():
        int_value = int(text)
        if 1 <= int_value <= 96:
            return int_value
        raise ValueError("Field 'SHAA' must be in range 1..96")

    match = re.fullmatch(r"(\d{1,2}):(\d{2})", text)
    if not match:
        raise ValueError("Field 'SHAA' must use HH:MM format")

    hour = int(match.group(1))
    minute = int(match.group(2))
    if not 0 <= hour <= 23:
        raise ValueError("Field 'SHAA' hour must be in range 0..23")
    if minute not in {0, 15, 30, 45}:
        raise ValueError("Field 'SHAA' minute must be one of 00, 15, 30, 45")

    return (hour * 4) + (minute // 15) + 1


def map_value_to_integer(
    value: object,
    mapping_dict: Dict[str, int | str],
    feature_name: str = "Unknown",
    default: int | str = 0
) -> ModelCode:
    """Convert a frontend selection key to the raw value the model expects."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    
    if feature_name == "SHAA":
        return _coerce_shaa(value)

    if isinstance(value, str):
        key = value.strip()
        if key in mapping_dict:
            return mapping_dict[key]

        normalized = _normalize_key(key)
        for candidate_key, candidate_value in mapping_dict.items():
            if _normalize_key(candidate_key) == normalized:
                return candidate_value
    
    if value in mapping_dict.values():
        return value

    if isinstance(value, (int, np.integer, float)):
        numeric_value = int(value)
        if numeric_value in mapping_dict.values():
            return numeric_value
    
    return default


def engineer_road_structure(
    df: pd.DataFrame,
    had_maslul_col: str = "HAD_MASLUL",
    rav_maslul_col: str = "RAV_MASLUL"
) -> pd.Series:
    """Return legacy numeric road codes; the saved model uses string categories instead."""
    road_structure = pd.Series(2, index=df.index, dtype=int)  # Default: two-way
    
    if had_maslul_col in df.columns:
        single_lane = (df[had_maslul_col] == 1)
        road_structure[single_lane] = 1
    
    if rav_maslul_col in df.columns:
        multi_lane = (df[rav_maslul_col] == 1)
        # Determine if multi-lane is one-way or two-way
        if had_maslul_col in df.columns:
            multi_lane_one_way = multi_lane & (df[had_maslul_col] == 1)
            road_structure[multi_lane_one_way] = 3
            road_structure[multi_lane & ~(df[had_maslul_col] == 1)] = 4
        else:
            road_structure[multi_lane] = 4
    
    # Mark truly missing values as unknown
    road_structure[df[[had_maslul_col, rav_maslul_col]].isna().all(axis=1)] = 0
    
    return road_structure


def prepare_model_input(
    ui_input: Dict[str, object],
    feature_order: Optional[List[str]] = None
) -> Dict[str, ModelCode]:
    """Map UI keys to model codes, preserving categorical strings and column order."""
    if _FEATURE_MAPPING_DB is None:
        raise RuntimeError("Authoritative feature mappings are unavailable or invalid")
    if feature_order is None:
        feature_order = list(FEATURE_ORDER)

    model_input: Dict[str, ModelCode] = {}

    for feature in feature_order:
        if feature not in FEATURE_CONFIG:
            raise ValueError(f"Unknown feature: {feature}")

        config = FEATURE_CONFIG[feature]
        if feature == "SHAA":
            model_input[feature] = _coerce_shaa(ui_input.get(feature))
            continue

        model_input[feature] = map_value_to_integer(
            ui_input.get(feature),
            config["mapping"],
            feature_name=feature,
            default=config["default"],
        )

    return model_input


def prepare_model_frame(
    ui_input: Dict[str, object],
    feature_order: Optional[List[str]] = None
) -> pd.DataFrame:
    """Convert UI input into a single-row DataFrame for the saved pipeline."""
    final_order = list(feature_order) if feature_order is not None else list(FEATURE_ORDER)
    model_input_dict = prepare_model_input(ui_input, final_order)
    return pd.DataFrame([[model_input_dict[feature] for feature in final_order]], columns=final_order)


def prepare_model_array(
    ui_input: Dict[str, object],
    feature_order: Optional[List[str]] = None
) -> np.ndarray:
    """Convert UI input to a numpy array for the model."""
    return prepare_model_frame(ui_input, feature_order).to_numpy(dtype=object)


def validate_ui_input(ui_input: Dict[str, object]) -> ValidationReport:
    """Validate UI input and return a report of errors, warnings, and missing features."""
    report: ValidationReport = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "missing_features": []
    }
    
    required_features = [
        'SHAA', 'HODESH_TEUNA', 'YOM_BASHAVUA', 'SUG_TEUNA',
        'ROAD_STRUCTURE', 'ROHAV', 'NAFA', 'ZURAT_ISHUV',
        'MEHIRUT_MUTERET', 'TEURA', 'SUG_DEREH', 'SIMUN_TIMRUR',
        'TKINUT', 'PNE_KVISH', 'MEZEG_AVIR', 'YOM_LAYLA'
    ]
    
    for feature in required_features:
        if feature not in ui_input or ui_input[feature] is None:
            report["missing_features"].append(feature)
            report["valid"] = False
    
    for feature, value in ui_input.items():
        if feature not in FEATURE_CONFIG:
            report["warnings"].append(f"Unknown feature: {feature}")
            continue
        
        config = FEATURE_CONFIG[feature]
        mapping = config["mapping"]
        
        if not isinstance(value, (str, int, float)) and value is not None:
            report["errors"].append(
                f"{feature}: Invalid value type {type(value).__name__}. Expected string, integer, or float."
            )
            report["valid"] = False
        elif feature == "SHAA":
            try:
                _coerce_shaa(value)
            except ValueError as exc:
                report["errors"].append(f"{feature}: {exc}")
                report["valid"] = False
        elif isinstance(value, str) and value not in mapping and _normalize_key(value) not in {_normalize_key(key) for key in mapping}:
            report["warnings"].append(
                f"{feature}: Value '{value}' not in mapping. Will use default."
            )
    
    return report


# Dataset preprocessing

def preprocess_dataset(
    df: pd.DataFrame,
    selected_features: Optional[List[str]] = None,
    target_column: str = "NIKVIYUT_TEUNA"
) -> pd.DataFrame:
    """Prepare legacy numeric data; this helper is not the final model training pipeline."""
    if selected_features is None:
        selected_features = list(FEATURE_ORDER)
    
    # Create a copy to avoid modifying original
    df_processed = df.copy()
    
    # Engineer ROAD_STRUCTURE if not present
    if 'ROAD_STRUCTURE' in selected_features and 'ROAD_STRUCTURE' not in df_processed.columns:
        if 'HAD_MASLUL' in df_processed.columns or 'RAV_MASLUL' in df_processed.columns:
            df_processed['ROAD_STRUCTURE'] = engineer_road_structure(df_processed)
        else:
            df_processed['ROAD_STRUCTURE'] = 0  # Default unknown
    
    # Select only required features
    available_features = [f for f in selected_features if f in df_processed.columns]
    if target_column in df_processed.columns:
        available_features.append(target_column)
    
    df_processed = df_processed[available_features]
    
    # Fill missing values with 0 (unknown)
    df_processed = df_processed.fillna(0)
    
    # Ensure all values are integers
    for col in selected_features:
        if col in df_processed.columns:
            df_processed[col] = df_processed[col].astype(int)
    
    # Remove rows with all zero values (completely missing)
    df_processed = df_processed[~(df_processed[selected_features] == 0).all(axis=1)]
    
    return df_processed


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("Data Mapper & Preprocessing Module")
    print("=" * 80)
    
    # Example 1: Map single value
    print("\n[Example 1] Mapping single values:")
    print(f"  'יבש' → {map_value_to_integer('יבש', ROAD_SURFACE_MAPPING, 'PNE_KVISH')}")
    print(f"  'עירוני בצומת' → {map_value_to_integer('עירוני בצומת', ROAD_TYPE_MAPPING, 'SUG_DEREH')}")
    
    # Example 2: Prepare model input from UI data
    print("\n[Example 2] Convert UI input to model input:")
    ui_data = {
        "SHAA": "14:00",
        "HODESH_TEUNA": "5",
        "YOM_BASHAVUA": "שני",
        "SUG_TEUNA": "חזיתי",
        "ROAD_STRUCTURE": "דו-כיווני",
        "ROHAV": "רחב (מעל 8 מ')",
        "NAFA": "דרום",
        "ZURAT_ISHUV": "עירוני",
        "MEHIRUT_MUTERET": "עד 80 קמ״ש",
        "TEURA": "אור יום",
        "SUG_DEREH": "עירוני בצומת",
        "SIMUN_TIMRUR": "בעל רמזור",
        "TKINUT": "תקין",
        "PNE_KVISH": "רטוב ממים",
        "MEZEG_AVIR": "גשום",
        "YOM_LAYLA": "יום",
    }
    
    model_input = prepare_model_input(ui_data)
    print("  Input Dictionary:")
    for k, v in list(model_input.items())[:5]:
        print(f"    {k}: {v}")
    print("  ...")
    
    # Example 3: Create numpy array for model
    print("\n[Example 3] Create prediction array:")
    model_array = prepare_model_array(ui_data)
    print(f"  Shape: {model_array.shape}")
    print(f"  Values: {model_array[:5]}...")
    
    # Example 4: Validate UI input
    print("\n[Example 4] Validate user input:")
    validation = validate_ui_input(ui_data)
    print(f"  Valid: {validation['valid']}")
    print(f"  Errors: {len(validation['errors'])}")
    print(f"  Warnings: {len(validation['warnings'])}")
    
    print("\n" + "=" * 80)
