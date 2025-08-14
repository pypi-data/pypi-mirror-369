from sqlalchemy import Boolean, Column, SmallInteger
from sqlalchemy.dialects.postgresql import JSON

from .base import Base, IdentityBase, TimeSign, Types


class RawMeasurement(IdentityBase, TimeSign, Base):
    __tablename__ = "measurement_raw"

    data = Column(JSON)
    type = Column(SmallInteger)
    is_processed = Column(Boolean, default=False)

    @property
    def type_enum(self):
        return Types(self.type)

    @type_enum.setter
    def type_enum(self, type_enum):
        self.type = type_enum.value
