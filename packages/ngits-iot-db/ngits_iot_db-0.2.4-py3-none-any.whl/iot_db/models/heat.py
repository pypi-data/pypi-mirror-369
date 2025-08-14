from sqlalchemy import UniqueConstraint

from .base import MeasurementBase, UsageBase


class HeatMeasurement(MeasurementBase):
    __tablename__ = "measurement_heat"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "measured_ts",
        ),
    )
    RAW_VALUE_ATTR_NAME = "total_energy_consumption_kwh"


class DailyHeatUsage(UsageBase):
    __tablename__ = "usage_heat_daily"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "consumption_ts",
        ),
    )


class MonthlyHeatUsage(UsageBase):
    __tablename__ = "usage_heat_monthly"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "consumption_ts",
        ),
    )
