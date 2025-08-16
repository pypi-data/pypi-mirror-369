from typing import ClassVar

from pydantic import Field, model_validator

from .base_api import BaseOneRosterModel


class Enrollment(BaseOneRosterModel["Enrollment"]):
    role: str | None
    user: dict | None
    class_id: dict | None = Field(None, alias="class")
    begin_date: str | None = Field(None, alias="beginDate")
    end_date: str | None = Field(None, alias="endDate")

    _resource_path: ClassVar[str] = "enrollment"

    @model_validator(mode="after")
    def extract_class_sourced_id(cls, values):
        data = values.class_id
        if isinstance(data, dict):
            values.class_id = data.get("sourcedId")
        return values

    @model_validator(mode="after")
    def extract_user_sourced_id(cls, values):
        data = values.user
        if isinstance(data, dict):
            values.user = data.get("sourcedId")
        return values
