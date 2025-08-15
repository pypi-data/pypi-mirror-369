from .classes.auth import Auth
from .classes.Students import Students
from .classes.Student import Student
from .classes.Teachers import Teachers
from .classes.Schools import Schools
from .classes.Demographics import Demographics
from .classes.AcademicSessions import AcademicSessions
from .classes.Courses import Courses
from .classes.Enrollments import Enrollments
from .classes.GradingPeriods import GradingPeriods
from .classes.Orgs import Orgs
from .classes.Terms import Terms
from .classes.Users import Users
import requests


class InfiniteCampus:
    """Python Object for Interacting with Infinite Campus.
    Requires token_url, key, secret, and base_url"""

    access_token: str
    url: str

    def __init__(self, token_url, key, secret, base_url):
        credentials = Auth(
            token_url,
            key,
            secret,
            base_url,
        )
        self.access_token = credentials.access_token
        self.url = credentials.base_url
        self.students = Students(api_call=self.api_call)
        self.student = Student(api_call=self.api_call)
        self.teachers = Teachers(api_call=self.api_call)
        self.schools = Schools(api_call=self.api_call)
        self.demographics = Demographics(api_call=self.api_call)
        self.academicSessions = AcademicSessions(api_call=self.api_call)
        self.courses = Courses(api_call=self.api_call)
        self.enrollments = Enrollments(api_call=self.api_call)
        self.gradingPeriods = GradingPeriods(api_call=self.api_call)
        self.orgs = Orgs(api_call=self.api_call)
        self.terms = Terms(api_call=self.api_call)
        self.users = Users(api_call=self.api_call)

    def api_call(self, endpoint, filters=""):
        token = self.access_token
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(
            f"{self.url}{endpoint}?filter={filters}&limit=5000", headers=headers
        )
        if r.status_code != 200:
            print(f"API Call returned {r.status_code} status")
            raise Exception(
                f"API endpoint {endpoint} returned a {r.status_code} Status Code."
            )
        return r.json()
