from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}