"""Classes."""

from typing import ClassVar

from pydantic import Field

from .base_api import BaseOneRosterModel


class Demographics(BaseOneRosterModel["Demographics"]):
    """Classes."""

    birth_date: str | None = Field(None, alias="birthDate")

    _resource_path: ClassVar[str] = "demographic"
