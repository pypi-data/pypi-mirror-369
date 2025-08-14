import logging
from typing import Tuple

from exasol.slc.api.push import push

from exasol.slc_ci.lib.ci_step_output_printer import (
    CIStepOutputPrinter,
    CIStepOutputPrinterProtocol,
)


class CIPush:

    def __init__(
        self, printer: CIStepOutputPrinterProtocol = CIStepOutputPrinter(logging.info)
    ):
        self._printer = printer

    def push(
        self,
        flavor_path: tuple[str, ...],
        target_docker_repository: str,
        target_docker_tag_prefix: str,
        docker_user: str,
        docker_password: str,
    ):
        """
        Push the docker image to Dockerhub
        """

        logging.info(f"Running command 'push' with parameters: {locals()}")
        push(
            flavor_path=flavor_path,
            push_all=True,
            force_push=True,
            workers=7,
            target_docker_repository_name=target_docker_repository,
            target_docker_tag_prefix=target_docker_tag_prefix,
            target_docker_username=docker_user,
            target_docker_password=docker_password,
            log_level="WARNING",
            use_job_specific_log_file=True,
        )
        self._printer.print_exasol_docker_images()
