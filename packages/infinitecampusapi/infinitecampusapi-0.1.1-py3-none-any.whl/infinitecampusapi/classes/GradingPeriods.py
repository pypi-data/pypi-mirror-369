from .AcademicSessions import AcademicSessionsModel
from pydantic import UUID4


class GradingPeriods:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_grading_periods(self) -> list[AcademicSessionsModel]:
        """Gets all gradingPeriods and returns a list of AcademicSessionsModel Objects"""
        r = self.api_call("gradingPeriods")
        periods = []
        for period in r["academicSessions"]:
            periods.append(AcademicSessionsModel(**period))
        return period

    def get_grading_period(self, pid: UUID4) -> AcademicSessionsModel:
        """Returns a single gradingPeriod of the AcademicSessionsModel type"""
        r = self.api_call(f"gradingPeriods/{pid}")
        period = AcademicSessionsModel(**r["academicSession"])
        return period
