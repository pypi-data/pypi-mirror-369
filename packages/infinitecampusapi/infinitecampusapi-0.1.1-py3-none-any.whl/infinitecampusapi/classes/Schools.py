from pydantic import UUID4, BaseModel
from datetime import datetime
from .Student import StudentModel
from .extras import guidRef
from .Classes import ScoreScales, ClassesModel, ClassGroup
from .Enrollments import EnrollmentsModel
from .Teachers import TeacherModel
from .Courses import CourseModel
from .AcademicSessions import AcademicSessionsModel


class SchoolModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastMofified: datetime | None = None
    metadata: dict = {}
    name: str
    identifier: str
    children: list[guidRef] = []
    parent: guidRef
    type: str


class Schools:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_school_score_scales(self, pid: UUID4) -> list[ScoreScales]:
        """Returns a list of ScoreScales for a school using it's SourcedID.
        I am unable to test this as I don't have a vendor header to use."""
        r = self.api_call(f"schools/{pid}/scoreScales")
        scales = []
        for scale in r["scoreScales"]:
            scales.append(ScoreScales(**scale))
        return scales

    def get_schools(self) -> list[SchoolModel]:
        """Returns a list of all schools"""
        r = self.api_call("schools")
        schools = []
        for school in r["orgs"]:
            schools.append(SchoolModel(**school))
        return schools

    def get_school_classes(self, pid: UUID4) -> list[ClassesModel]:
        """Returns a list of Classes for a school"""
        r = self.api_call(f"schools/{pid}/classes")
        classes = []
        for s_class in r["classes"]:
            classes.append(ClassesModel(**s_class))
        return classes

    def get_school_class_enrollments(
        self, pid: UUID4, class_pid: UUID4
    ) -> list[EnrollmentsModel]:
        """Returns a list of Enrollments for a class in a school"""
        r = self.api_call(f"schools/{pid}/classes/{class_pid}/enrollments")
        enrollments = []
        for enrollment in r["enrollments"]:
            enrollments.append(
                EnrollmentsModel(s_class=enrollment["class"], **enrollment)
            )
        return enrollments

    def get_school_class_students(
        self, pid: UUID4, class_pid: UUID4
    ) -> list[StudentModel]:
        """Returns a list of Students for a class in a school"""
        r = self.api_call(f"schools/{pid}/classes/{class_pid}/students")
        students = []
        for student in r["users"]:
            students.append(StudentModel(**student))
        return students

    def get_school_class_teachers(
        self, pid: UUID4, class_pid: UUID4
    ) -> list[TeacherModel]:
        """Returns a list of Students for a class in a school"""
        r = self.api_call(f"schools/{pid}/classes/{class_pid}/teachers")
        teachers = []
        for teacher in r["users"]:
            teachers.append(TeacherModel(**teacher))
        return teachers

    def get_school_class_groups(self, pid: UUID4) -> list[ClassGroup]:
        """Returns a list of Class groups for a school"""
        r = self.api_call(f"schools/{pid}/classGroups")
        groups = []
        for group in r["classGroups"]:
            groups.append(ClassGroup(**group))
        return groups

    def get_school_courses(self, pid: UUID4) -> list[CourseModel]:
        """Returns a list of Courses  for a school"""
        r = self.api_call(f"schools/{pid}/courses")
        courses = []
        for course in r["courses"]:
            courses.append(CourseModel(**course))
        return courses

    def get_school_enrollments(self, pid: UUID4) -> list[EnrollmentsModel]:
        """Returns a list of Enrollments  for a school"""
        r = self.api_call(f"schools/{pid}/enrollments")
        enrollments = []
        for enrollment in r["enrollments"]:
            enrollments.append(
                EnrollmentsModel(s_class=enrollment["class"], **enrollment)
            )
        return enrollments

    def get_school(self, pid: UUID4) -> SchoolModel:
        """Returns information about a school using it's SourcedID"""
        r = self.api_call(f"schools/{pid}")
        return SchoolModel(**r["org"])

    def get_school_students(self, pid: UUID4) -> list[StudentModel]:
        """Returns a list of Students by School"""
        r = self.api_call(f"schools/{pid}/students")
        students = []
        for student in r["users"]:
            students.append(StudentModel(**student))
        return students

    def get_school_teachers(self, pid: UUID4) -> list[TeacherModel]:
        """Returns a list of Teachers by School"""
        r = self.api_call(f"schools/{pid}/teachers")
        teachers = []
        for teacher in r["users"]:
            teachers.append(TeacherModel(**teacher))
        return teachers

    def get_school_terms(self, pid: UUID4) -> list[AcademicSessionsModel]:
        """Returns a list of terms by School"""
        r = self.api_call(f"schools/{pid}/terms")
        terms = []
        for term in r["academicSessions"]:
            terms.append(AcademicSessionsModel(**term))
        return terms
