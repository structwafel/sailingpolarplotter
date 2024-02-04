from pydantic import BaseModel


class BoatPlotterConfig(BaseModel):
    name: str
    original_points: bool
    degree: int
    min_true_winds: int
    max_true_winds: int
    even: bool
    uneven: bool
    exclude: list[int]


class JsonInputData(BaseModel):
    data: str
    config: BoatPlotterConfig
