"""
.. module: meteor.auth.service
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import HTTPException, Depends
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from sqlalchemy import select, insert, update
from sqlalchemy.exc import IntegrityError
from meteor.auth.schema import UserCreate, UserOrganization, UserRegister, UserUpdate

from meteor.config import (
    METEOR_AUTHENTICATION_PROVIDER_SLUG,
    METEOR_AUTHENTICATION_DEFAULT_USER,
)
from meteor.database.core import DbSession
from meteor.enums import UserRoles
from meteor.organization import service as organization_service
from meteor.organization.models import OrganizationRead
from meteor.plugins.base import plugins

from .models import (
    MeteorUser,
    MeteorUserOrganization,
)

log = logging.getLogger(__name__)

InvalidCredentialException = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
)


async def get(*, db_session: DbSession, user_id: UUID) -> Optional[MeteorUser]:
    """Returns a user based on the given user id."""
    return await db_session.scalar(select(MeteorUser).where(MeteorUser.id == user_id))


async def get_by_email(*, db_session: DbSession, email: str) -> Optional[MeteorUser]:
    """Returns a user object based on user email."""
    return await db_session.scalar(select(MeteorUser).where(MeteorUser.email == email))


async def create_or_update_organization_role(*, db_session: DbSession, user: MeteorUser, role_in: UserOrganization):
    """Creates a new organization role or updates an existing role."""
    if not role_in.organization.id:
        organization = await organization_service.get_by_name(db_session=db_session, name=role_in.organization.name)
        organization_id = organization.id
    else:
        organization_id = role_in.organization.id

    # organization_role = (
    #     db_session.query(MeteorUserOrganization)
    #     .filter(
    #         MeteorUserOrganization.meteor_user_id == user.id,
    #     )
    #     .filter(MeteorUserOrganization.organization_id == organization_id)
    #     .one_or_none()
    # )
    organization_role = await db_session.scalar(
        select(MeteorUserOrganization).where(
            MeteorUserOrganization.meteor_user_id == user.id,
            MeteorUserOrganization.organization_id == organization_id,
        )
    )

    if not organization_role:
        return MeteorUserOrganization(
            organization_id=organization.id,
            role=role_in.role,
        )

    organization_role.role = role_in.role
    return organization_role


async def create(*, db_session: DbSession, organization: str, user_in: (UserRegister | UserCreate)) -> MeteorUser:
    """Creates a new meteor user."""
    # pydantic forces a string password, but we really want bytes
    password = bytes(user_in.password, "utf-8")

    # create the user
    user = MeteorUser(
        **user_in.model_dump(exclude={"password", "organizations", "projects", "role"}), password=password
    )

    org = await organization_service.get_by_slug_or_raise(
        db_session=db_session,
        organization_in=OrganizationRead(name=organization, slug=organization),
    )

    # add user to the current organization
    role = UserRoles.member
    if hasattr(user_in, "role"):
        role = user_in.role

    user.organizations.append(MeteorUserOrganization(organization=org, role=role))

    return db_session.scalar(insert(MeteorUser).values(user).returning(MeteorUser))


async def get_or_create(*, db_session: DbSession, organization: str, user_in: UserRegister) -> MeteorUser:
    """Gets an existing user or creates a new one."""
    user = await get_by_email(db_session=db_session, email=user_in.email)

    if not user:
        try:
            user = await create(db_session=db_session, organization=organization, user_in=user_in)
        except IntegrityError:
            log.exception(f"Unable to create user with email address {user_in.email}.")

    return user


async def update_user(*, db_session: DbSession, user_in: UserUpdate) -> MeteorUser:
    """Updates a user."""

    update_data = MeteorUser(user_in.model_dump(exclude={"password", "organizations", "projects"}, skip_defaults=True))


    if user_in.password:
        update_data.password = bytes(user_in.password, "utf-8")

    if user_in.organizations:
        roles = []

        for role in user_in.organizations:
            roles.append(create_or_update_organization_role(db_session=db_session, user=update_data, role_in=role))

    return db_session.scalar(update(MeteorUser).where(MeteorUser.id == user_in.id).values(update_data).returning(MeteorUser))


async def get_current_user(request: Request) -> MeteorUser:
    """Attempts to get the current user depending on the configured authentication provider."""
    if METEOR_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(METEOR_AUTHENTICATION_PROVIDER_SLUG)
        user_email = auth_plugin.get_current_user(request)
    else:
        log.debug("No authentication provider. Default user will be used")
        user_email = METEOR_AUTHENTICATION_DEFAULT_USER

    if not user_email:
        log.exception(
            f"Unable to determine user email based on configured auth provider or no default auth user email defined. Provider: {METEOR_AUTHENTICATION_PROVIDER_SLUG}"
        )
        raise InvalidCredentialException

    return get_or_create(
        db_session=request.state.db,
        organization=request.state.organization,
        user_in=UserRegister(email=user_email),
    )


CurrentUser = Annotated[MeteorUser, Depends(get_current_user)]


async def get_current_role(request: Request, current_user: MeteorUser = Depends(get_current_user)) -> UserRoles:
    """Attempts to get the current user depending on the configured authentication provider."""
    return current_user.get_organization_role(organization_slug=request.state.organization)
