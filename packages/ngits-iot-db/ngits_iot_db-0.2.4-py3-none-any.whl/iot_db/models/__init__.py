"""IoT Database Models - SQLAlchemy models for IoT sensor data storage."""

from .alert import Alert, AlertDefinition
from .base import AlertBase, AlertLevels, AlertTypes, MeasurementBase, Types, Units
from .electricity import (
    DailyElectricityUsage,
    ElectricityMeasurement,
    MonthlyElectricityUsage,
)
from .heat import DailyHeatUsage, HeatMeasurement, MonthlyHeatUsage
from .raw import RawMeasurement
from .temperature import TemperatureMeasurement
from .water import DailyWaterUsage, MonthlyWaterUsage, WaterMeasurement

__all__ = [
    "Alert",
    "AlertDefinition",
    "AlertLevels",
    "AlertTypes",
    "DailyElectricityUsage",
    "DailyHeatUsage",
    "DailyWaterUsage",
    "ElectricityMeasurement",
    "HeatMeasurement",
    "map_daily_usage_class",
    "map_measurement_class",
    "map_monthly_usage_class",
    "MonthlyElectricityUsage",
    "MonthlyHeatUsage",
    "MonthlyWaterUsage",
    "RawMeasurement",
    "TemperatureMeasurement",
    "Types",
    "Units",
    "WaterMeasurement",
]


def map_measurement_class(type_: Types):
    match type_:
        case Types.electricity:
            return ElectricityMeasurement
        case Types.water:
            return WaterMeasurement
        case Types.heat:
            return HeatMeasurement
        case Types.temperature:
            return TemperatureMeasurement
        case _:
            raise NotImplementedError


def map_daily_usage_class(type_: Types):
    match type_:
        case Types.electricity:
            return DailyElectricityUsage
        case Types.water:
            return DailyWaterUsage
        case Types.heat:
            return DailyHeatUsage
        case Types.temperature:
            return None
        case _:
            raise NotImplementedError


def map_monthly_usage_class(type_: Types):
    match type_:
        case Types.electricity:
            return MonthlyElectricityUsage
        case Types.water:
            return MonthlyWaterUsage
        case Types.heat:
            return MonthlyHeatUsage
        case Types.temperature:
            return None
        case _:
            raise NotImplementedError
