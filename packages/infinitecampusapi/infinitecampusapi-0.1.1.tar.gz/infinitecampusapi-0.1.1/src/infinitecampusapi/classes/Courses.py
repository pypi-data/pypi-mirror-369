from pydantic import BaseModel, UUID4
from .extras import guidRef
from .Classes import ClassesModel
from datetime import datetime


class CourseModel(BaseModel):
    sourcedId: UUID4 | str
    status: str
    dateLastModified: datetime
    metadata: dict = {}
    title: str
    courseCode: str
    subjects: list[str] = []
    subjectCodes: list[str] = []
    org: guidRef


class Courses:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_courses(self) -> list[CourseModel]:
        """Returns a list of courses using the CourseModel"""
        r = self.api_call("courses")
        courses = []
        for course in r["courses"]:
            courses.append(CourseModel(**course))
        return courses

    def get_course(self, pid: UUID4) -> CourseModel:
        """Returns a single course using the CourseModel Type"""
        r = self.api_call(f"courses/{pid}")
        return CourseModel(**r["course"])

    def get_course_classes(self, pid: UUID4 | str) -> ClassesModel:
        """Returns a list of classes for a course using the ClassesModel Type"""
        r = self.api_call(f"courses/{pid}/classes")
        classes = []
        for s_class in r["classes"]:
            classes.append(ClassesModel(**s_class))
        return classes
