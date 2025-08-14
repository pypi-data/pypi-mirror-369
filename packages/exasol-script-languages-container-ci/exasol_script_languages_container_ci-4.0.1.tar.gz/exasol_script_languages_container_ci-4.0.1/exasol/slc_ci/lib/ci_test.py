import logging
from pathlib import Path
from typing import Optional, Protocol, Tuple

from exasol.slc.api.run_db_tests import run_db_test
from exasol.slc.models.accelerator import Accelerator
from exasol.slc.models.test_result import AllTestsResult

from exasol.slc_ci.lib.ci_step_output_printer import (
    CIStepOutputPrinter,
    CIStepOutputPrinterProtocol,
)


class DBTestRunnerProtocol(Protocol):
    def run(
        self,
        flavor_path: tuple[str, ...],
        release_goal: tuple[str, ...],
        test_file: tuple[str, ...],
        test_folder: tuple[str, ...],
        test_container_folder: str,
        generic_language_tests: tuple[str, ...],
        accelerator: Accelerator,
        source_docker_tag_prefix: str,
        source_docker_repository_name: str,
        workers: int,
        docker_username: Optional[str],
        docker_password: Optional[str],
        use_existing_container: Optional[str],
    ) -> AllTestsResult:
        raise NotImplementedError()


class DBTestRunner(DBTestRunnerProtocol):
    def run(
        self,
        flavor_path: tuple[str, ...],
        release_goal: tuple[str, ...],
        test_file: tuple[str, ...],
        test_folder: tuple[str, ...],
        test_container_folder: str,
        generic_language_tests: tuple[str, ...],
        accelerator: Accelerator,
        source_docker_tag_prefix: str,
        source_docker_repository_name: str,
        workers: int,
        docker_username: Optional[str],
        docker_password: Optional[str],
        use_existing_container: Optional[str],
    ) -> AllTestsResult:
        return run_db_test(
            flavor_path=flavor_path,
            release_goal=release_goal,
            test_file=test_file,
            test_folder=test_folder,
            test_container_folder=test_container_folder,
            generic_language_test=generic_language_tests,
            accelerator=accelerator,
            source_docker_tag_prefix=source_docker_tag_prefix,
            source_docker_repository_name=source_docker_repository_name,
            workers=workers,
            source_docker_username=docker_username,
            source_docker_password=docker_password,
            log_level="WARNING",
            use_job_specific_log_file=True,
            use_existing_container=use_existing_container,
        )


class CIExecuteTest:

    def __init__(
        self,
        db_test_runner: DBTestRunnerProtocol = DBTestRunner(),
        printer: CIStepOutputPrinterProtocol = CIStepOutputPrinter(logging.info),
    ):
        self._db_test_runner = db_test_runner
        self._printer = printer

    def execute_tests(
        self,
        flavor_path: tuple[str, ...],
        slc_path: Path,
        goal: str,
        test_files: tuple[str, ...],
        test_folders: tuple[str, ...],
        generic_language_tests: tuple[str, ...],
        accelerator: Accelerator,
        docker_user: str,
        docker_password: str,
        test_container_folder: str,
        commit_sha: str,
        build_docker_repository: str,
    ):
        """
        Run db tests
        """
        db_tests_are_ok = self._run_db_tests(
            flavor_path=flavor_path,
            goal=goal,
            slc_path=slc_path,
            test_files=test_files,
            test_folders=test_folders,
            generic_language_tests=generic_language_tests,
            accelerator=accelerator,
            docker_user=docker_user,
            docker_password=docker_password,
            test_container_folder=test_container_folder,
            commit_sha=commit_sha,
            build_docker_repository=build_docker_repository,
        )
        self._printer.print_exasol_docker_images()
        if not db_tests_are_ok:
            raise AssertionError("Not all tests are ok!")

    def _run_db_tests(
        self,
        flavor_path: tuple[str, ...],
        slc_path: Path,
        goal: str,
        test_files: tuple[str, ...],
        test_folders: tuple[str, ...],
        generic_language_tests: tuple[str, ...],
        accelerator: Accelerator,
        docker_user: str,
        docker_password: str,
        test_container_folder: str,
        commit_sha: str,
        build_docker_repository: str,
    ) -> bool:
        logging.info(f"Running command 'run_db_test' for flavor-path {flavor_path}")
        db_test_result = self._db_test_runner.run(
            flavor_path=flavor_path,
            test_file=test_files,
            test_folder=test_folders,
            release_goal=(goal,),
            generic_language_tests=generic_language_tests,
            accelerator=accelerator,
            source_docker_tag_prefix=commit_sha,
            source_docker_repository_name=build_docker_repository,
            workers=7,
            docker_username=docker_user,
            docker_password=docker_password,
            test_container_folder=test_container_folder,
            use_existing_container=str(slc_path),
        )
        self._printer.print_file(db_test_result.command_line_output_path)
        return db_test_result.tests_are_ok
