from datetime import datetime
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo
from fastapi.encoders import jsonable_encoder
from pydantic import ConfigDict, model_validator
from sqlalchemy import Column, DateTime, Integer, event
from sqlalchemy.dialects.postgresql import UUID

def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")

class MeteorBase(object):
    """Base class for all models"""
    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any]:
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }

        return {**data, **datetime_fields}

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)

class UUIDMixin(object):
    """UUID mixin"""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

class IncrementalMixin(object):
    """ID mixin"""
    id = Column(Integer, primary_key=True, autoincrement=True)   

class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)

class DeletedMixin(object):
    """Soft delete mixin"""

    deleted_at = Column(DateTime)
    deleted_at._creation_order = 9999

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._deleted_at)

    @staticmethod
    def _deleted_at(mapper, connection, target):
        target.deleted_at = datetime.utcnow()

