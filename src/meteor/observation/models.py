from sqlalchemy import Column, String, LargeBinary, Integer, Float
from sqlalchemy.sql.schema import ForeignKey

from meteor.database.core import Base
from meteor.models import IncrementalMixin, MeteorBase, TimeStampMixin
from meteor.organization.models import Organization
from sqlalchemy.orm import relationship

class ObservationElement(Base, IncrementalMixin):
    __table_args__ = {"schema": "meteor_core"}

    name = Column(String, unique=True)
    abbreviation = Column(String, nullable=True)
    description = Column(String, nullable=True)
    unit = Column(String, nullable=False)
    scale = Column(Float, default=1)


class ObservationValue(Base, IncrementalMixin, TimeStampMixin):
    observation_element_id = Column(Integer, ForeignKey(ObservationElement.id))
    value = Column(LargeBinary, nullable=False)
    organization_id = Column(Integer, ForeignKey(Organization.id), primary_key=True)
    organization = relationship(Organization, backref="ObservationValue")


class ObservationRead(MeteorBase):
    name: str
    unit: str
    value: str