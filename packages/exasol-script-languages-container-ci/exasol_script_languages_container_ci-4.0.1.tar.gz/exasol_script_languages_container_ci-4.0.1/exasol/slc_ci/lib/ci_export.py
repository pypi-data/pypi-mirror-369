import logging
from pathlib import Path
from typing import Tuple

from exasol.slc.api import export

from exasol.slc_ci.lib.ci_step_output_printer import (
    CIStepOutputPrinter,
    CIStepOutputPrinterProtocol,
)


class CIExport:

    def __init__(
        self, printer: CIStepOutputPrinterProtocol = CIStepOutputPrinter(logging.info)
    ):
        self._printer = printer

    def export(
        self, flavor_path: tuple[str, ...], goal: str, output_directory: str
    ) -> Path:
        """
        Export the flavor as tar.gz file.
        The returned path is the path of the tar.gz file.
        """

        logging.info(f"Running command 'export' with parameters: {locals()}")
        export_result = export(
            flavor_path=flavor_path,
            workers=7,
            log_level="WARNING",
            use_job_specific_log_file=True,
            release_goal=(goal,),
            output_directory=output_directory,
        )
        self._printer.print_exasol_docker_images()
        export_infos = list(export_result.export_infos.values())
        if len(export_infos) != 1:
            raise RuntimeError(f"Unexpected number of export infos")
        export_info = export_infos[0]
        export_flavor_infos = list(export_info.values())
        if len(export_flavor_infos) != 1:
            raise RuntimeError(f"Unexpected number of export flavor infos")

        export_flavor_info = export_flavor_infos[0]
        return Path(export_flavor_info.cache_file)
