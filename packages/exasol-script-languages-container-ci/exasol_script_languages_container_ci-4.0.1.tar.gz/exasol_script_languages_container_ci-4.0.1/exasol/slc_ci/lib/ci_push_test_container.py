import logging
from typing import Optional

from exasol.slc.internal.tasks.test.test_container_content import (
    build_test_container_content,
)
from exasol_integration_test_docker_environment.lib.api import push_test_container

from exasol.slc_ci.lib.ci_step_output_printer import (
    CIStepOutputPrinter,
    CIStepOutputPrinterProtocol,
)


class CIPushTestContainer:

    def __init__(
        self, printer: CIStepOutputPrinterProtocol = CIStepOutputPrinter(logging.info)
    ):
        self._printer = printer

    def push_test_container(
        self,
        build_docker_repository: Optional[str],
        force: bool,
        commit_sha: str,
        docker_user: str,
        docker_password: str,
        test_container_folder: str,
    ):
        """
        Push the test container with given commit SHA.
        """

        logging.info(
            f"Running command 'push_test_container' with parameters: {locals()}"
        )
        content = build_test_container_content(test_container_folder)
        test_container_image_infos = push_test_container(
            force_push=force,
            workers=7,
            test_container_content=content,
            target_docker_repository_name=build_docker_repository,
            target_docker_tag_prefix=commit_sha,
            target_docker_username=docker_user,
            target_docker_password=docker_password,
            log_level="WARNING",
            use_job_specific_log_file=True,
        )
        self._printer.print_exasol_docker_images()
