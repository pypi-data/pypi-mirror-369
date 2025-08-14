from sqlalchemy import UniqueConstraint

from .base import MeasurementBase, UsageBase


class TemperatureMeasurement(MeasurementBase):
    __tablename__ = "measurement_temperature"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "measured_ts",
        ),
    )
    RAW_VALUE_ATTR_NAME = "total_degc"
