from pydantic import BaseModel, UUID4
from .extras import guidRef
from datetime import datetime


class EnrollmentsModel(BaseModel):
    sourcedId: UUID4 | str
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    role: str
    primary: bool | None = None
    beginDate: datetime = ""
    endDate: datetime = ""
    user: guidRef
    s_class: guidRef
    school: guidRef


class Enrollments:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_enrollments(self) -> list[EnrollmentsModel]:
        """Returns a list of enrollments using the enrollmentModel"""
        r = self.api_call("enrollments")
        enrollments = []
        for enrollment in r["enrollments"]:
            enrollments.append(
                EnrollmentsModel(s_class=enrollment["class"], **enrollment)
            )
        return enrollments

    def get_enrollment(self, pid: UUID4) -> EnrollmentsModel:
        """Returns a single enrollment using the enrollmentModel Type"""
        r = self.api_call(f"enrollments/{pid}")
        return EnrollmentsModel(s_class=r["enrollment"]["class"], **r["enrollment"])
