from pydantic import BaseModel, UUID4, EmailStr
from .extras import guidRef, UserId, V1P2UserRoleBase
from datetime import datetime


class UsersModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict
    userMasterIdentifier: str = ""
    identifier: str = ""
    username: int
    enabledUser: bool
    phone: str = ""
    sms: str = ""
    givenName: str
    familyName: str
    middleName: str = ""
    preferredFirstName: str = ""
    preferredLastName: str = ""
    preferredMiddleName: str = ""
    email: EmailStr | str = ""
    userIds: list[UserId] = []
    roles: list[V1P2UserRoleBase] = []
    agents: list[guidRef] = []
    grades: list[str] = []


class Users:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_users(self) -> list[UsersModel]:
        """Returns a list of users using the UsersModel"""
        r = self.api_call("users")
        users = []
        for user in r["users"]:
            users.append(UsersModel(**user))
        return users

    def get_user(self, pid: UUID4) -> UsersModel:
        r = self.api_call(f"users/{pid}")
        return UsersModel(**r["user"])

    def get_user_classes(self, pid: UUID4):
        r = self.api_call(f"users/{pid}/classes")
        return r
