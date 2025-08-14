import logging
from pathlib import Path
from typing import List

from exasol.slc_ci.lib.get_build_config_model import get_build_config_model
from exasol.slc_ci.lib.git_access import GitAccess
from exasol.slc_ci.lib.github_access import GithubAccess
from exasol.slc_ci.model.build_mode import BuildMode
from exasol.slc_ci.model.github_event import GithubEvent


def get_all_affected_files(
    git_access: GitAccess, base_ref: str, remote: str
) -> list[Path]:
    complete_base_ref = f"{remote}/{base_ref}" if remote else base_ref
    base_last_commit_sha = git_access.get_head_commit_sha_of_branch(complete_base_ref)
    changed_files = set()  # type: ignore
    for commit in git_access.get_last_commits():
        if commit == base_last_commit_sha:
            break
        changed_files.update(git_access.get_files_of_commit(commit))
    return [Path(changed_file) for changed_file in changed_files]


def _run_check_if_need_to_build(
    base_ref: str, remote: str, flavor: str, git_access: GitAccess
) -> BuildMode:
    build_config = get_build_config_model()
    if "[rebuild]" in git_access.get_last_commit_message():
        return BuildMode.REBUILD
    affected_files = list(get_all_affected_files(git_access, base_ref, remote))
    logging.debug(
        f"check_if_need_to_build: Found files of last commits: {affected_files}"
    )
    affected_files = [
        file
        for file in affected_files
        if not any(
            [
                file.is_relative_to(ignore_path)
                for ignore_path in build_config.ignore_paths
            ]
        )
    ]

    if len(affected_files) > 0:
        # Now filter out also other flavor folders
        this_flavor_path = build_config.flavors_path / flavor
        affected_files = [
            file
            for file in affected_files
            if (
                file.is_relative_to(this_flavor_path)
                or not file.is_relative_to(build_config.flavors_path)
            )
        ]
    logging.debug(f"check_if_need_to_build: filtered files: {affected_files}")
    return BuildMode.NORMAL if len(affected_files) > 0 else BuildMode.NO_BUILD_NEEDED


def check_if_need_to_build(
    base_ref: str,
    remote: str,
    flavor: str,
    github_event: GithubEvent,
    github_access: GithubAccess,
    git_access: GitAccess,
) -> None:
    """
    Checks which build type is required considering:
    - Github Push event: => A complete rebuild is required.
                         Push events are filtered for special branches (main/master/develop)
                         by the Github workflows.
    - Github Pull Request event:
      - Compare the changed files of the PR if they affect the current flavor:
         - If yes => a normal build (no force rebuild) is required.
         - If no => no need to build and test the flavor.
    """
    if github_event == GithubEvent.PULL_REQUEST:
        mode = _run_check_if_need_to_build(base_ref, remote, flavor, git_access)
        github_access.write_result(mode.value)
    elif github_event == GithubEvent.PUSH:
        github_access.write_result(BuildMode.REBUILD.value)
    else:
        raise ValueError("unknown github event")
