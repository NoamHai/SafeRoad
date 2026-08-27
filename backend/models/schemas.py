from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
