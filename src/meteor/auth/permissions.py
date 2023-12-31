import logging
from abc import ABC, abstractmethod

from fastapi import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from meteor.auth.service import get_current_user
from meteor.enums import UserRoles, Visibility
from meteor.models import PrimaryKeyModel
from meteor.organization import service as organization_service
from meteor.organization.models import OrganizationRead

log = logging.getLogger(__name__)


def any_permission(permissions: list, request: Request) -> bool:
    for p in permissions:
        try:
            p(request=request)
            return True
        except HTTPException:
            pass
    return False


class BasePermission(ABC):
    """
    Abstract permission that all other Permissions must be inherited from.

    Defines basic error message, status & error codes.

    Upon initialization, calls abstract method  `has_required_permissions`
    which will be specific to concrete implementation of Permission class.

    You would write your permissions like this:

    .. code-block:: python

        class TeapotUserAgentPermission(BasePermission):

            def has_required_permissions(self, request: Request) -> bool:
                return request.headers.get('User-Agent') == "Teapot v1.0"

    """

    org_error_msg = [{"msg": "Organization not found. Please, contact your Meteor admin."}]
    org_error_code = HTTP_404_NOT_FOUND

    user_error_msg = [{"msg": "User not found. Please, contact your Meteor admin"}]
    user_error_code = HTTP_404_NOT_FOUND

    user_role_error_msg = [
        {
            "msg": "Your user doesn't have permissions to create, update, or delete this resource. Please, contact your Meteor admin."
        }
    ]
    user_role_error_code = HTTP_403_FORBIDDEN

    role = None

    @abstractmethod
    def has_required_permissions(self, request: Request) -> bool:
        ...

    def __init__(self, request: Request):
        organization = None
        if request.path_params.get("organization"):
            organization = organization_service.get_by_slug_or_raise(
                db_session=request.state.db,
                organization_in=OrganizationRead(
                    slug=request.path_params["organization"],
                    name=request.path_params["organization"],
                ),
            )
        elif request.path_params.get("organization_id"):
            organization = organization_service.get(
                db_session=request.state.db, organization_id=request.path_params["organization_id"]
            )

        if not organization:
            raise HTTPException(status_code=self.org_error_code, detail=self.org_error_msg)

        user = get_current_user(request=request)
        if not user:
            raise HTTPException(status_code=self.user_error_code, detail=self.user_error_msg)

        self.role = user.get_organization_role(organization.slug)
        if not self.has_required_permissions(request):
            raise HTTPException(status_code=self.user_role_error_code, detail=self.user_role_error_msg)


class PermissionsDependency(object):
    """
    Permission dependency that is used to define and check all the permission
    classes from one place inside route definition.

    Use it as an argument to FastAPI's `Depends` as follows:

    .. code-block:: python

        app = FastAPI()

        @app.get(
            "/teapot/",
            dependencies=[Depends(
                PermissionsDependency([TeapotUserAgentPermission]))]
        )
        async def teapot() -> dict:
            return {"teapot": True}
    """

    def __init__(self, permissions_classes: list):
        self.permissions_classes = permissions_classes

    def __call__(self, request: Request):
        for permission_class in self.permissions_classes:
            permission_class(request=request)


class OrganizationOwnerPermission(BasePermission):
    def has_required_permissions(self, request: Request) -> bool:
        return self.role == UserRoles.owner


class OrganizationManagerPermission(BasePermission):
    def has_required_permissions(self, request: Request) -> bool:
        permission = any_permission(
            permissions=[
                OrganizationOwnerPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.manager:
                return True
        return permission


class OrganizationAdminPermission(BasePermission):
    def has_required_permissions(self, request: Request) -> bool:
        permission = any_permission(
            permissions=[
                OrganizationOwnerPermission,
                OrganizationManagerPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.admin:
                return True
        return permission


class OrganizationMemberPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        permission = any_permission(
            permissions=[
                OrganizationOwnerPermission,
                OrganizationManagerPermission,
                OrganizationAdminPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.member:
                return True
        return permission
