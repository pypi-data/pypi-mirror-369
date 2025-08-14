from sqlalchemy import UniqueConstraint

from .base import MeasurementBase, UsageBase


class WaterMeasurement(MeasurementBase):
    __tablename__ = "measurement_water"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "measured_ts",
        ),
    )
    RAW_VALUE_ATTR_NAME = "total_m3"


class DailyWaterUsage(UsageBase):
    __tablename__ = "usage_water_daily"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "consumption_ts",
        ),
    )


class MonthlyWaterUsage(UsageBase):
    __tablename__ = "usage_water_monthly"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "consumption_ts",
        ),
    )
