import logging
from typing import Optional, Tuple

from exasol.slc.api import build

from exasol.slc_ci.lib.ci_step_output_printer import (
    CIStepOutputPrinter,
    CIStepOutputPrinterProtocol,
)


class CIBuild:

    def __init__(
        self, printer: CIStepOutputPrinterProtocol = CIStepOutputPrinter(logging.info)
    ):
        self._printer = printer

    def build(
        self,
        flavor_path: tuple[str, ...],
        rebuild: bool,
        build_docker_repository: Optional[str],
        docker_user: str,
        docker_password: str,
    ):
        """
        Build the script-language container for given flavor.
        """

        logging.info(f"Running command 'build' with parameters: {locals()}")
        if build_docker_repository is None:
            slc_image_infos = build(
                flavor_path=flavor_path,
                force_rebuild=rebuild,
                source_docker_username=docker_user,
                source_docker_password=docker_password,
                shortcut_build=False,
                workers=7,
                log_level="WARNING",
                use_job_specific_log_file=True,
            )
        else:
            slc_image_infos = build(
                flavor_path=flavor_path,
                force_rebuild=rebuild,
                source_docker_repository_name=build_docker_repository,
                source_docker_username=docker_user,
                source_docker_password=docker_password,
                shortcut_build=False,
                workers=7,
                log_level="WARNING",
                use_job_specific_log_file=True,
            )
        self._printer.print_exasol_docker_images()
