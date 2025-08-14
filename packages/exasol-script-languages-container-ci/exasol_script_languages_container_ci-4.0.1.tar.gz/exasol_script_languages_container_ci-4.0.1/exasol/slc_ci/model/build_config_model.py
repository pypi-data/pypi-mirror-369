import pathlib
from pathlib import Path
from typing import List

from pydantic import BaseModel


class BuildConfig(BaseModel):

    @property
    def flavors_path(self):
        return Path("flavors")

    ignore_paths: list[pathlib.Path]

    docker_build_repository: str
    docker_release_repository: str
    test_container_folder: str
