import re
from dataclasses import dataclass


@dataclass(frozen=True)
class BuildActions:
    push_to_docker_release_repo: bool


@dataclass(frozen=True)
class BranchConfig:
    main = BuildActions(push_to_docker_release_repo=True)
    other = BuildActions(push_to_docker_release_repo=False)


def _get_branch_config(branch_name: str) -> BuildActions:
    matches = ((re.compile(r"refs/heads/(master|main)"), BranchConfig.main),)

    branch_cfg = BranchConfig.other
    for branch_regex, branch_config in matches:
        if branch_regex.match(branch_name):
            branch_cfg = branch_config
            break
    return branch_cfg


def push_to_docker_release_repo(branch_name: str) -> bool:
    return _get_branch_config(branch_name).push_to_docker_release_repo
