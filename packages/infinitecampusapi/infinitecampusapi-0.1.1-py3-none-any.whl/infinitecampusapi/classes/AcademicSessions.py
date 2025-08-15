from pydantic import BaseModel, UUID4
from .extras import guidRef
from datetime import datetime


class AcademicSessionsModel(BaseModel):
    sourcedId: UUID4 | int
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    title: str
    schoolYear: str
    startDate: datetime = ""
    endDate: datetime = ""
    children: list[guidRef] = []
    parent: guidRef = {}
    type: str


class AcademicSessions:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_academic_sessions(self) -> list[AcademicSessionsModel]:
        """Gets all AcademicSessions and returns a list of AcademicSessionsModel Objects"""
        r = self.api_call("academicSessions")
        sessions = []
        for session in r["academicSessions"]:
            sessions.append(AcademicSessionsModel(**session))
        return sessions

    def get_academic_session(self, pid: UUID4) -> AcademicSessionsModel:
        """Returns a single academicSession of the AcademicSessionsModel type"""
        r = self.api_call(f"academicSessions/{pid}")
        session = AcademicSessionsModel(**r["academicSession"])
        return session
