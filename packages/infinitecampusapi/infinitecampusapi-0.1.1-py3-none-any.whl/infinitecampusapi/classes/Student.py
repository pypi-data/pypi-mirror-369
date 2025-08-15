from pydantic import BaseModel, UUID4, PositiveInt, EmailStr
from datetime import datetime
from .Demographics import Demographics, DemographicsModel
from .extras import guidRef, V1P2UserRoleBase, UserId


class StudentModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict
    userMasterIdentifier: PositiveInt
    identifier: PositiveInt
    username: PositiveInt
    enabledUser: bool
    phone: str = ""
    sms: str = ""
    givenName: str
    familyName: str
    middleName: str = ""
    preferredFirstName: str = ""
    preferredLastName: str = ""
    preferrredMiddleName: str = ""
    email: EmailStr | None = None
    userIds: list[UserId] = []
    roles: list[V1P2UserRoleBase] = []
    agents: list[guidRef] = []
    grades: list[str] = []


class Student:

    def __init__(self, api_call):
        self.api_call = api_call

    def get_student(self, pid: UUID4) -> StudentModel:
        r = self.api_call(f"students/{pid}")
        return StudentModel(**r["user"])

    def get_student_classes(self, pid: UUID4):
        r = self.api_call(f"students/{pid}/classes")
        return r

    def get_student_demographics(self, student: StudentModel) -> DemographicsModel:
        """Convenience function to get the demographics for a student.
        Takes a StudentModel object as the input and returns a DemographicsModel Object
        """
        student_demographic = Demographics(api_call=self.api_call)
        demographics = student_demographic.get_demographic(student.sourcedId)
        return demographics
