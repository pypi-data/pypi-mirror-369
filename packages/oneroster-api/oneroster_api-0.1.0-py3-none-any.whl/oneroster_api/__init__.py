"""Init."""

from pathlib import Path

from .academic_sessions import AcademicSessions
from .classes import Classes
from .client import set_credentials
from .courses import Courses
from .demographics import Demographics
from .enrollments import Enrollment
from .users import User

__all__ = [
    "AcademicSessions",
    "Classes",
    "Courses",
    "Demographics",
    "Enrollment",
    "User",
    "set_credentials",
]


def import_oneroster_data(import_dir: Path = Path()) -> None:
    """Uses api to import all oneroster data."""
    User.download_all(import_dir)
    AcademicSessions.download_all(import_dir)
    Classes.download_all(import_dir)
    Demographics.download_all(import_dir)
    Courses.download_all(import_dir)
    Enrollment.download_all(import_dir)
