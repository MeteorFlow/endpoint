import logging
from typing import List, Optional
from pydantic.errors import PydanticErrorMixin
from sqlalchemy.orm import Session
from sqlalchemy import insert, select

from meteor.database.manage import init_schema
from meteor.enums import UserRoles
from meteor.exceptions import NotFoundError

from .models import ObservationElement, ObservationRead, ObservationValue

log = logging.getLogger(__name__)


async def get_observation_elements(*, db_session: Session) -> List[Optional[ObservationElement]]:
    """
    Gets all elements in the database.
    """
    return await db_session.execute(select(ObservationElement)).scalar().all()


async def get_element_by_id(*, db_session: Session, element_id) -> Optional[ObservationElement]:
    """ """
    return await db_session.execute(select(ObservationElement).where(ObservationElement.id == element_id).limit(1))


async def get_element_by_exact_name(*, db_session: Session, element_name) -> Optional[ObservationElement]:
    """
    Gets all elements in the database.
    """
    return await db_session.execute(select(ObservationElement).where(ObservationElement.name == element_name))


async def get_observation_value(*, db_session: Session, element_id, organization_id) -> Optional[ObservationRead]:
    """
    Gets all elements in the database.
    """
    data = await db_session.execute(
        select(ObservationValue).where(
            ObservationValue.organization_id == organization_id
            and ObservationValue.observation_element_id == element_id
        ).
    )
