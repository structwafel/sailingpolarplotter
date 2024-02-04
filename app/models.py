from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Method(str, Enum):
    regression = "regression"
    moving_average = "moving_average"


class BoatPlotterConfig(BaseModel):
    name: str
    degree: int
    original_points: bool
    smooth_plot: bool
    to_zero: bool
    method: Method


class InputData(BaseModel):
    data: str
    config: BoatPlotterConfig


class JsonBoatPlotterConfig(BaseModel):
    name: str
    original_points: bool
    smooth_plot: bool
    degree: int
    method: Method
    min_true_winds: int
    max_true_winds: int
    even: bool
    uneven: bool
    exclude: Optional[list[int]]


class JsonInputData(BaseModel):
    data: str
    config: JsonBoatPlotterConfig
