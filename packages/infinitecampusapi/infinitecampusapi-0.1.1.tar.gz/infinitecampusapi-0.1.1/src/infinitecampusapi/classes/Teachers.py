from pydantic import BaseModel, UUID4, EmailStr
from datetime import datetime
from .extras import guidRef, V1P2UserRoleBase, UserId


class TeacherModel(BaseModel):
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
    email: EmailStr = ""
    userIds: list[UserId] = []
    roles: list[V1P2UserRoleBase] = []
    agents: list[guidRef] = []
    grades: list[str] = []


class Teachers:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_teachers(self) -> list[TeacherModel]:
        """Gets all teachers and returns a list of TeacherModel Objects"""
        r = self.api_call("teachers")
        teachers = []
        for teacher in r["users"]:
            teachers.append(TeacherModel(**teacher))
        return teachers

    def get_teacher(self, pid: UUID4) -> TeacherModel:
        """Returns a single teacher of the TeacherModel type"""
        r = self.api_call(f"teachers/{pid}")
        teacher = TeacherModel(**r["user"])
        return teacher

    def get_teacher_ids(self):
        """This is deprecated for use with v1p1"""
        data = []
        r = self.get_teachers()
        for user in r["users"]:
            sourcedid = user["sourcedId"]
            name = f"{user['givenName']} {user['familyName']}"
            if sourcedid[0] == "t":
                sourcedid = f"{sourcedid[1:]}"
            sourcedid = int(sourcedid)
            data.append({"name": name, "ID": f"{sourcedid:04}"})
        return data

    def get_class_teacher(self, sourcedId: UUID4):
        r = self.api_call(f"classes/{sourcedId}/teachers")
        return r["users"][0]
