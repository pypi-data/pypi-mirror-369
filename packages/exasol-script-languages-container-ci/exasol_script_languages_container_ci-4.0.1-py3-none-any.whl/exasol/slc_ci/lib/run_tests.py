import logging
from pathlib import Path

from exasol.slc_ci.lib.ci_prepare import CIPrepare
from exasol.slc_ci.lib.ci_test import CIExecuteTest
from exasol.slc_ci.lib.get_build_config_model import get_build_config_model
from exasol.slc_ci.lib.get_flavor_ci_model import get_flavor_ci_model


def run_tests(
    flavor: str,
    slc_directory: str,
    test_set_name: str,
    docker_user: str,
    docker_password: str,
    commit_sha: str,
    ci_prepare: CIPrepare = CIPrepare(),
    ci_test: CIExecuteTest = CIExecuteTest(),
) -> None:
    logging.info(f"Run tests for parameters: {locals()}")
    build_config = get_build_config_model()
    flavor_config = get_flavor_ci_model(build_config, flavor)
    matched_test_set = [
        test_set
        for test_set in flavor_config.test_config.test_sets
        if test_set.name == test_set_name
    ]
    if len(matched_test_set) != 1:
        raise ValueError(f"Invalid test set name: {test_set_name}")
    test_set_files = tuple(matched_test_set[0].files)
    test_set_folders = tuple(matched_test_set[0].folders)
    is_files_folders = test_set_files and test_set_folders
    if is_files_folders:
        raise ValueError("Both test_files and test_folders cannot be set")
    goal = matched_test_set[0].goal
    generic_language_tests = matched_test_set[0].generic_language_tests
    accelerator = matched_test_set[0].accelerator
    slc_path = Path(slc_directory)
    if not slc_path.exists():
        raise ValueError(f"{slc_path} does not exist")
    slc_files = list(slc_path.glob(f"{flavor}*.tar.gz"))
    if len(slc_files) != 1:
        raise ValueError(
            f"{slc_directory} does not contain expected tar.gz file, but \n {slc_files}"
        )
    slc_file_path = slc_files[0]

    flavor_path = (f"{build_config.flavors_path}/{flavor}",)
    test_container_folder = build_config.test_container_folder

    ci_prepare.prepare(commit_sha=commit_sha)
    if test_set_files:
        ci_test.execute_tests(
            flavor_path=flavor_path,
            slc_path=slc_file_path,
            goal=goal,
            test_files=test_set_files,
            test_folders=(),
            generic_language_tests=(),
            accelerator=accelerator,
            test_container_folder=test_container_folder,
            docker_user=docker_user,
            docker_password=docker_password,
            commit_sha=commit_sha,
            build_docker_repository=build_config.docker_build_repository,
        )
    elif test_set_folders:
        ci_test.execute_tests(
            flavor_path=flavor_path,
            slc_path=slc_file_path,
            goal=goal,
            test_files=(),
            test_folders=test_set_folders,
            generic_language_tests=(),
            accelerator=accelerator,
            test_container_folder=test_container_folder,
            docker_user=docker_user,
            docker_password=docker_password,
            commit_sha=commit_sha,
            build_docker_repository=build_config.docker_build_repository,
        )

    if generic_language_tests:
        ci_test.execute_tests(
            flavor_path=flavor_path,
            slc_path=slc_file_path,
            goal=goal,
            test_files=(),
            test_folders=(),
            generic_language_tests=tuple(generic_language_tests),
            accelerator=accelerator,
            test_container_folder=test_container_folder,
            docker_user=docker_user,
            docker_password=docker_password,
            commit_sha=commit_sha,
            build_docker_repository=build_config.docker_build_repository,
        )
