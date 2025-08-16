"""Users."""

from typing import Any, ClassVar

from pydantic import Field, model_validator

from .base_api import BaseOneRosterModel


class User(BaseOneRosterModel["User"]):
    """User Object."""

    username: int | None
    status: str | None
    role: str | None
    enabled: bool | None = Field(None, alias="enabledUser")
    state_id: list | None = Field(None, alias="userIds")
    first_name: str | None = Field(None, alias="givenName")
    last_name: str | None = Field(None, alias="familyName")
    middle_name: str | None = Field(None, alias="middleName")
    email: str | None
    identifier: int | None
    grades: list | None
    metadata: dict | None

    _resource_path: ClassVar[str] = "user"

    @model_validator(mode="after")
    def extract_grade(cls, values: Any) -> Any:
        """Extracts grade from list."""
        if values.role == "student":
            values.grades = values.grades[0]
        return values

    @model_validator(mode="after")
    def extract_state_id(cls, values: Any) -> Any:
        """Returns the state id from dict."""
        if values.role == "student":
            data = values.state_id
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item["type"] == "SSID":
                        values.state_id = item.get("identifier")
        elif values.role == "teacher":
            data = values.metadata
            if isinstance(data, dict):
                values.state_id = data.get("stateId")
        else:
            values.state_id = None

        return values
