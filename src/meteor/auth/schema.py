

from typing import List
from uuid import UUID

from typing import Optional
from pydantic import field_validator, field_validator, Field
from pydantic.networks import EmailStr

from meteor.auth.utils import generate_password, hash_password

from meteor.models import MeteorBase, Pagination
from meteor.organization.models import OrganizationRead

class UserOrganization(MeteorBase):
    organization: OrganizationRead
    default: Optional[bool] = False
    role: Optional[str] = Field(None, nullable=True)


class UserBase(MeteorBase):
    email: EmailStr
    organizations: Optional[List[UserOrganization]] = []

    @field_validator("email")
    def email_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v


class UserLogin(UserBase):
    password: str

    @field_validator("password")
    def password_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserRegister(UserLogin):
    password: Optional[str] = Field(None, nullable=True)

    @field_validator("password", mode="before")
    def password_required(cls, v):
        # we generate a password for those that don't have one
        password = v or generate_password()
        return hash_password(password)


class UserLoginResponse(MeteorBase):
    token: Optional[str] = Field(None, nullable=True)


class UserRead(UserBase):
    id: UUID
    role: Optional[str] = Field(None, nullable=True)
    experimental_features: Optional[bool]


class UserUpdate(MeteorBase):
    id: UUID
    password: Optional[str] = Field(None, nullable=True)
    organizations: Optional[List[UserOrganization]]
    experimental_features: Optional[bool]
    role: Optional[str] = Field(None, nullable=True)

    @field_validator("password", mode="before")
    def hash(cls, v):
        return hash_password(str(v))


class UserCreate(MeteorBase):
    email: EmailStr
    password: Optional[str] = Field(None, nullable=True)
    # organizations: Optional[List[UserOrganization]]
    role: Optional[str] = Field(None, nullable=True)

    @field_validator("password", mode="before")
    def hash(cls, v):
        return hash_password(str(v))


class UserRegisterResponse(MeteorBase):
    token: Optional[str] = Field(None, nullable=True)


class UserPagination(Pagination):
    items: List[UserRead] = []