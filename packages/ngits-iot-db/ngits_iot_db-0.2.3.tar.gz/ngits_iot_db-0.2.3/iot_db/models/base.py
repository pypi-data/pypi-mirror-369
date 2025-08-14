from datetime import datetime
from enum import Enum as PyEnum
from enum import IntEnum

from sqlalchemy import Column, DateTime, Float, Integer, SmallInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class Units(PyEnum):
    m3 = "m3"
    kwh = "kwh"
    degc = "degc"


class Types(IntEnum):
    water = 1
    electricity = 2
    heat = 3
    temperature = 4


class AlertTypes(IntEnum):
    # Value-based alerts
    threshold_high = 1  # Upper threshold breach
    threshold_low = 2  # Lower threshold breach
    sudden_change = 3  # Sudden value change detection

    # Data availability alerts
    offline = 10  # Device not responding
    data_gap = 11  # Gap in data transmission
    data_delayed = 12  # Delayed data reception

    # Data quality alerts
    invalid_reading = 20  # Invalid measurement detected
    stuck_value = 21  # Value not changing over extended period
    noise = 22  # Excessive fluctuations in measurements


class AlertLevels(IntEnum):
    emergency = 0  # Highest priority - immediate action required (safety threats)
    critical = 1  # Requires immediate response (e.g. 24h data loss)
    warning = 2  # Requires attention (e.g. data delay > 1h)
    info = 3  # Informational (minor deviations from norm)


class TimeSign(Base):
    __abstract__ = True

    created_ts = Column(DateTime, default=datetime.utcnow)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IdentityBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    tenant = Column(UUID(as_uuid=True))
    external_id = Column(Text, nullable=True)
    meter_id = Column(Text)


class MeasurementBase(IdentityBase, TimeSign, Base):
    __abstract__ = True

    measured_ts = Column(DateTime)
    value = Column(Float)


class UsageBase(IdentityBase, TimeSign, Base):
    __abstract__ = True

    start_ts = Column(DateTime)
    end_ts = Column(DateTime)
    consumption_ts = Column(DateTime)

    start_value = Column(Float)
    end_value = Column(Float)
    consumption = Column(Float)


class AlertBase(IdentityBase, TimeSign, Base):
    __abstract__ = True

    _type = Column("type", SmallInteger)
    _level = Column("level", SmallInteger)
    device_name = Column(Text)

    @hybrid_property
    def type(self):
        return AlertTypes(self._type) if self._type is not None else None

    @type.setter
    def type(self, value):
        self._type = value.value if value is not None else None

    @hybrid_property
    def level(self):
        return AlertLevels(self._level) if self._level is not None else None

    @level.setter
    def level(self, value):
        self._level = value.value if value is not None else None
