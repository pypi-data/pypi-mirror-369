import json
from typing import List

from exasol.slc_ci.lib.get_build_config_model import get_build_config_model
from exasol.slc_ci.lib.github_access import GithubAccess


def get_flavors(github_access: GithubAccess) -> None:
    build_config = get_build_config_model()
    if not build_config.flavors_path.exists():
        raise ValueError(f"Flavor path '{build_config.flavors_path}' does not exist")
    flavors: list[str] = list()
    for p in build_config.flavors_path.iterdir():
        if p.is_dir():
            flavors.append(p.name)

    github_access.write_result(json.dumps(flavors))
