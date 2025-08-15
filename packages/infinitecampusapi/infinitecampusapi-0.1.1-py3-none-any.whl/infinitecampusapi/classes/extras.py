from pydantic import BaseModel, UUID4
from datetime import datetime


class guidRef(BaseModel):
    href: str = ""
    sourcedId: UUID4 | str = ""
    type: str = ""


class V1P2UserRoleBase(BaseModel):
    beginDate: datetime = ""
    endDate: datetime = ""
    roleType: str = ""
    role: str = ""
    org: guidRef = ""


class UserId(BaseModel):
    identifier: str = ""
    type: str = ""
