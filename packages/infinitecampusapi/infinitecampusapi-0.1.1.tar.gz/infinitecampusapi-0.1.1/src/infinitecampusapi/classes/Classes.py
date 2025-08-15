from pydantic import BaseModel, UUID4
from datetime import datetime
from .extras import guidRef


class CategoriesModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    title: str
    weight: float


class LineItemsModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    title: str
    description: str
    assignDate: datetime
    dueDate: datetime
    resultValueMin: float
    resultValueMax: float
    s_class: guidRef = {}
    category: guidRef
    gradingPeriod: guidRef
    school: guidRef
    academicSession: guidRef
    scoreScale: guidRef


class ResultsModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    score: float
    textScore: str
    scoreDate: datetime
    comment: str
    scoreStatus: str
    missing: str
    incomplete: str
    late: str
    inProgress: str
    s_class: guidRef = {}
    student: guidRef = {}
    lineItem: guidRef = {}


class ScoreScales(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    title: str
    type: str
    s_class: guidRef = {}
    course: guidRef = {}
    scoreScaleValue: list = []


class ClassesModel(BaseModel):
    sourcedId: UUID4 | str = ""
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    title: str
    classType: str
    classCode: str
    location: str = ""
    subjects: list = []
    course: guidRef = {}
    school: guidRef = {}
    terms: list = []
    subjectCodes: list = []
    periods: list = []


class ClassGroup(BaseModel):
    sourcedId: UUID4 | str
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    title: str
    classes: list[guidRef] = []
    groupType: str


class Classes:
    def __init__(self, api_call):
        self.api_call = api_call
