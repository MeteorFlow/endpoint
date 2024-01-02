from sqlalchemy import DateTime, Column, String, LargeBinary, Integer, Boolean
from sqlalchemy.sql.schema import ForeignKey
from meteor.models import IncrementalMixin, MeteorBase, TimeStampMixin


class ObservationBase(MeteorBase):
    __table_args__ = {"schema": "meteor_core"}

class ObservationElement(ObservationBase, IncrementalMixin):
    name = Column(String, unique=True)
    abbreviation = Column(String, nullable=True)
    description = Column(String, nullable=True)
    unit = Column(String, nullable=False)

class ObservationValue(ObservationBase, IncrementalMixin, TimeStampMixin):
    observation_element_id = Column(Integer, ForeignKey("meteor_core.observation_element.id"))
    value = Column(LargeBinary, nullable=False)