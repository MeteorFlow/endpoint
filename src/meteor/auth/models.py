
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import UUID

import bcrypt
from jose import jwt
from typing import Optional
from pydantic import field_validator, field_validator, Field
from pydantic.networks import EmailStr

from sqlalchemy import DateTime, Column, String, LargeBinary, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils import TSVectorType

from meteor.config import (
    METEOR_JWT_SECRET,
    METEOR_JWT_ALG,
    METEOR_JWT_EXP,
)
from meteor.database.core import Base
from meteor.enums import UserRoles
from meteor.models import OrganizationSlug, TimeStampMixin, MeteorBase, Pagination, UUIDMixin
from meteor.organization.models import Organization, OrganizationRead


class MeteorUser(Base, TimeStampMixin, UUIDMixin):
    __table_args__ = {"schema": "meteor_core"}

    email = Column(String, unique=True)
    password = Column(LargeBinary, nullable=False)
    last_mfa_time = Column(DateTime, nullable=True)
    experimental_features = Column(Boolean, default=False)

    # relationships
    # events = relationship("Event", backref="meteor_user")

    search_vector = Column(TSVectorType("email", regconfig="pg_catalog.simple", weights={"email": "A"}))

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    @property
    def token(self):
        now = datetime.utcnow()
        exp = (now + timedelta(seconds=METEOR_JWT_EXP)).timestamp()
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, METEOR_JWT_SECRET, algorithm=METEOR_JWT_ALG)

    def get_organization_role(self, organization_slug: OrganizationSlug):
        """Gets the user's role for a given organization slug."""
        for o in self.organizations:
            if o.organization.slug == organization_slug:
                return o.role


class MeteorUserOrganization(Base, TimeStampMixin):
    __table_args__ = {"schema": "meteor_core"}
    meteor_user_id = Column(UUID(as_uuid=True), ForeignKey(MeteorUser.id), primary_key=True)
    meteor_user = relationship(MeteorUser, backref="organizations")

    organization_id = Column(Integer, ForeignKey(Organization.id), primary_key=True)
    organization = relationship(Organization, backref="users")

    role = Column(String, default=UserRoles.member)



