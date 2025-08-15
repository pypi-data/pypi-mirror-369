from .AcademicSessions import AcademicSessionsModel
from .Classes import ClassesModel
from pydantic import UUID4


class Terms:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_terms(self) -> list[AcademicSessionsModel]:
        """Gets all Terms and returns a list of AcademicSessionsModel Objects"""
        r = self.api_call("terms")
        terms = []
        for term in r["academicSessions"]:
            terms.append(AcademicSessionsModel(**term))
        return term

    def get_term(self, pid: UUID4) -> AcademicSessionsModel:
        """Returns a single Term of the AcademicSessionsModel type"""
        r = self.api_call(f"terms/{pid}")
        term = AcademicSessionsModel(**r["academicSession"])
        return term

    def get_term_classes(self, pid: UUID4) -> ClassesModel:
        """Returns a list of classes of the ClassesModel type"""
        r = self.api_call(f"terms/{pid}/classes")
        classes = []
        for s_class in r["classes"]:
            classes.append(ClassesModel(**s_class))
        return classes

    def get_term_grading_periods(self, pid: UUID4) -> AcademicSessionsModel:
        """Returns a list of AcademicSessions of the AcademisSessionsModel type"""
        r = self.api_call(f"terms/{pid}/gradingPeriods")
        sessions = []
        for session in r["academicSessions"]:
            sessions.append(AcademicSessionsModel(**session))
        return sessions
