"""
| Copyright 2017-2024, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import datetime
import enum

import pydantic
from fiftyone_helpers.utils import generate_slug


class UserRole(str, enum.Enum):
    """Serializable user role options"""

    ADMIN = "ADMIN"
    COLLABORATOR = "COLLABORATOR"
    DEMO = "DEMO"
    GUEST = "GUEST"
    MEMBER = "MEMBER"

class Organization(pydantic.BaseModel):
    """The common organization model"""

    id: str
    name: str
    display_name: str | None = None
    logo_url: str | None = None
    pypi_token: str | None = None

class User(pydantic.BaseModel):
    """The common user model"""

    id: str
    organization: Organization
    role: UserRole
    email: str
    name: str | None
    picture: str | None
    group_ids: list[str] = pydantic.Field(default_factory=list)

class Group(pydantic.BaseModel):
    """The common group model."""

    created_at: datetime.datetime | None
    created_by: str | None
    description: str | None
    id: str
    name: str
    org_id: str
    user_ids: list[str] = pydantic.Field(default_factory=list)

    @property
    def slug(self):
        return generate_slug(self.name)
