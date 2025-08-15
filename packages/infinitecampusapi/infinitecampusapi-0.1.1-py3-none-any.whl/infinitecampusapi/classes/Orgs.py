from pydantic import BaseModel, UUID4
from .extras import guidRef
from datetime import datetime


class OrgsModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    name: str
    identifier: str
    children: list[guidRef] = []
    parent: guidRef = {}
    type: str


class Orgs:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_orgs(self) -> list[OrgsModel]:
        """Gets all Orgs and returns a list of OrgsModel Objects"""
        r = self.api_call("orgs")
        orgs = []
        for org in r["orgs"]:
            orgs.append(OrgsModel(**org))
        return org

    def get_org(self, pid: UUID4) -> OrgsModel:
        """Returns a single org of the OrgsModel type"""
        r = self.api_call(f"orgs/{pid}")
        org = OrgsModel(**r["org"])
        return org
