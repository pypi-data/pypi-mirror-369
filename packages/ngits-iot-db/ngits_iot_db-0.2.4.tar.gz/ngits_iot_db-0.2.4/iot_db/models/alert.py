from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON

from .base import AlertBase


class AlertDefinition(AlertBase):
    __tablename__ = "alert_definition"

    device_name = Column(Text)
    properties = Column(JSON)
    receivers = Column(JSON)


class Alert(AlertBase):
    __tablename__ = "alert"

    detected_ts = Column(DateTime, nullable=False)
    active_marker = Column(Boolean, nullable=True)
    resolved_ts = Column(DateTime, nullable=True)

    details = Column(JSON)

    alert_definition_id = Column(Integer, ForeignKey("alert_definition.id"))

    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
            "type",
            "level",
            "active_marker",
            name="unique_active_alert_per_device",
        ),
    )
