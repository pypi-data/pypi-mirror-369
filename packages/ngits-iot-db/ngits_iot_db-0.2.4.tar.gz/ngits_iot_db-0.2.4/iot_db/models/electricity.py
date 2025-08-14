from sqlalchemy import UniqueConstraint

from .base import MeasurementBase, UsageBase


class ElectricityMeasurement(MeasurementBase):
    __tablename__ = "measurement_electricity"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "measured_ts",
        ),
    )

    RAW_VALUE_ATTR_NAME = "total_energy_consumption_kwh"


class DailyElectricityUsage(UsageBase):
    __tablename__ = "usage_electricity_daily"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "consumption_ts",
        ),
    )


class MonthlyElectricityUsage(UsageBase):
    __tablename__ = "usage_electricity_monthly"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "consumption_ts",
        ),
    )
