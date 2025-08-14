import logging
from pathlib import Path
from typing import Tuple

from exasol.slc.api import security_scan

from exasol.slc_ci.lib.ci_step_output_printer import (
    CIStepOutputPrinter,
    CIStepOutputPrinterProtocol,
)


class CISecurityScan:

    def __init__(
        self, printer: CIStepOutputPrinterProtocol = CIStepOutputPrinter(logging.info)
    ):
        self._printer = printer

    def run_security_scan(self, flavor_path: tuple[str, ...]):
        """
        Run security scan and print result
        """

        logging.info(f"Running command 'security_scan' with parameters {locals()}")
        security_scan_result = security_scan(
            flavor_path=flavor_path,
            workers=7,
            log_level="WARNING",
            use_job_specific_log_file=True,
        )
        logging.info("============= SECURITY REPORT ===========")
        self._printer.print_file(Path(security_scan_result.report_path))
        self._printer.print_exasol_docker_images()
        if not security_scan_result.scans_are_ok:
            raise AssertionError("Some security scans not successful.")
