from sqlalchemy import Column, String

from meteor.database.core import Base
from meteor.models import UUIDMixin


class MeteorAppSetting(Base, UUIDMixin):
    __table_args__ = {"schema": "meteor_core"}
    key = Column(String(255))
    value = Column(String(255))
    description = Column(String(1023))
    type = Column(String(255))
