from pydantic import BaseModel, UUID4
from datetime import datetime


class DemographicsModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    birthDate: datetime = ""
    sex: str
    countryOfBirthCode: str = ""
    stateOfBirthAbbreviation: str = ""
    cityOfBirth: str = ""
    publicSchoolResidenceStatus: str = ""
    americanIndianOrAlaskaNative: bool
    asian: bool
    blackOrAfricanAmerican: bool
    demographicRaceTwoOrMoreRaces: bool
    hispanicOrLatinoEthnicity: bool
    nativeHawaiianOrOtherPacificIslander: bool
    white: bool


class Demographics:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_demographics(self) -> list[DemographicsModel]:
        """Gets all demographics and returns a list of DemogrphicsModel Objects"""
        r = self.api_call("demographics")
        Demographics = []
        for Demographic in r["demographics"]:
            Demographics.append(DemographicsModel(**Demographic))
        return Demographics

    def get_demographic(self, pid: UUID4) -> DemographicsModel:
        """Returns a single Demographic of the DemographicModel type"""
        r = self.api_call(f"demographics/{pid}")
        Demographic = DemographicsModel(**r["demographics"])
        return Demographic
