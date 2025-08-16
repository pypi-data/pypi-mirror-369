"""Base API class."""

from pathlib import Path
from typing import ClassVar

import pandas as pd
from pydantic import BaseModel, Field

from . import client


class BaseOneRosterModel[T: BaseOneRosterModel](BaseModel):
    """Base API Class instance."""

    sourced_id: str | None = Field(None, alias="sourcedId")
    _resource_path: ClassVar[str] = ""

    @classmethod
    def retrieve_one(cls: type[T], resource_id: str) -> T:
        """Return individual resource."""
        response = client.get_request(f"{cls._resource_path}s/{resource_id}")
        response.raise_for_status()
        return cls(**response.json()[cls._resource_path])

    @classmethod
    def retrieve_all(cls: type[T]) -> list[T]:
        """Return list of type of class."""
        resource_path = f"{cls._resource_path}s"
        if cls._resource_path == "class":
            resource_path = "classes"

        response = client.get_request(resource_path)
        response.raise_for_status()
        return [cls(**item) for item in response.json()[resource_path]]
        # return response.json()

    @classmethod
    def download_all(cls: type[T], download_dir: Path = Path()) -> None:
        """Retrieve resource list and download csv to dir."""
        resource_path = f"{cls._resource_path}s"
        if cls._resource_path == "class":
            resource_path = "classes"

        response = client.get_request(resource_path)
        response.raise_for_status()
        resource_list = [cls(**item) for item in response.json()[resource_path]]

        # print(f"{resource_path}:\n{response.json()[resource_path][10]}\n\n")

        resource_df = pd.DataFrame([resource.__dict__ for resource in resource_list])
        resource_df.to_csv(download_dir / f"{resource_path}.csv", index=False)
