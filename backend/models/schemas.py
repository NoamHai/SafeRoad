from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_payload(cls, values: Any) -> Any:
        """Fill in the 16 features when an older 6-field payload is received."""
        if not isinstance(values, dict):
            return values

        if any(key in values for key in {"road_type", "weather", "time_of_day", "lighting", "junction", "road_surface"}):
            normalized = dict(values)
            time_of_day = str(values.get("time_of_day", "")).strip().lower()
            lighting = str(values.get("lighting", "")).strip().lower()
            weather = str(values.get("weather", "")).strip().lower()
            road_type = str(values.get("road_type", "")).strip().lower()
            junction = str(values.get("junction", "")).strip().lower()
            road_surface = str(values.get("road_surface", "")).strip().lower()

            normalized.setdefault("SHAA", "12:00" if time_of_day == "day" else "22:00")
            normalized.setdefault("HODESH_TEUNA", 1)
            normalized.setdefault("YOM_BASHAVUA", 1)
            normalized.setdefault("SUG_TEUNA", "other")
            normalized.setdefault("ROAD_STRUCTURE", "other")
            normalized.setdefault("ROHAV", "other")
            normalized.setdefault("NAFA", "unknown")
            normalized.setdefault(
                "ZURAT_ISHUV",
                "urban_intersection"
                if road_type in {"urban", "city"} and junction not in {"no_junction", "false", "0"}
                else (
                    "urban_non_intersection"
                    if road_type in {"urban", "city"}
                    else ("non_urban_intersection" if junction not in {"no_junction", "false", "0"} else "non_urban_non_intersection")
                ),
            )
            normalized.setdefault("MEHIRUT_MUTERET", "50")
            normalized.setdefault(
                "TEURA",
                "daylight"
                if lighting in {"daylight", "day"} or time_of_day == "day"
                else (
                    "night_with_working_lighting"
                    if lighting == "night_with_lighting"
                    else ("night_without_lighting" if lighting == "night_without_lighting" else "unknown_daylight_conditions")
                ),
            )
            normalized.setdefault(
                "SUG_DEREH",
                "urban_intersection"
                if road_type in {"urban", "city"} and junction not in {"no_junction", "false", "0"}
                else (
                    "urban_non_intersection"
                    if road_type in {"urban", "city"}
                    else ("non_urban_intersection" if junction not in {"no_junction", "false", "0"} else "non_urban_non_intersection")
                ),
            )
            normalized.setdefault("SIMUN_TIMRUR", "unknown")
            normalized.setdefault("TKINUT", "normal")
            normalized.setdefault(
                "PNE_KVISH",
                "dry"
                if road_surface == "dry"
                else (
                    "wet"
                    if road_surface == "wet"
                    else ("muddy" if road_surface == "mud" else ("covered_with_fuel" if road_surface == "fuel" else "unknown"))
                ),
            )
            normalized.setdefault(
                "MEZEG_AVIR",
                "clear"
                if weather == "clear"
                else ("rainy" if weather == "rainy" else ("foggy" if weather == "foggy" else ("hot_and_dry" if weather == "hot_and_dry" else "unknown"))),
            )
            normalized.setdefault("YOM_LAYLA", "day" if time_of_day == "day" else ("night" if time_of_day == "night" else "day"))
            return normalized

        return values

    SHAA: int | str = Field(...)
    HODESH_TEUNA: int | str = Field(...)
    YOM_BASHAVUA: int | str = Field(...)
    SUG_TEUNA: int | str = Field(...)
    ROAD_STRUCTURE: int | str = Field(...)
    ROHAV: int | str = Field(...)
    NAFA: int | str = Field(...)
    ZURAT_ISHUV: int | str = Field(...)
    MEHIRUT_MUTERET: int | str = Field(...)
    TEURA: int | str = Field(...)
    SUG_DEREH: int | str = Field(...)
    SIMUN_TIMRUR: int | str = Field(...)
    TKINUT: int | str = Field(...)
    PNE_KVISH: int | str = Field(...)
    MEZEG_AVIR: int | str = Field(...)
    YOM_LAYLA: int | str = Field(...)


# Response schema
class ModelResult(BaseModel):
    prediction: int
    prediction_label: str
    light_probability: float
    dangerous_probability: float